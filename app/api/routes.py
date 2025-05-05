# app/api/routes.py
from flask import Blueprint, request, jsonify
import crochet
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy import signals
from scrapy.signalmanager import dispatcher
import logging
import time
import traceback

from app.scrapers.content_spider import ContentSpider
from app.api.validators import validate_scrape_request

# Create logger
logger = logging.getLogger(__name__)

# Create a Blueprint for the API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/scrape', methods=['POST'])
def scrape_url():
    """Endpoint to scrape content from a URL"""
    data = request.get_json()
    
    # Validate request data
    validation_result = validate_scrape_request(data)
    if validation_result:
        logger.warning(f"Validation failed: {validation_result}")
        return jsonify({'error': validation_result}), 400
    
    url = data['url']
    config = data.get('config', {})
    output = []
    scrape_complete = [False]  # Using a list to create a mutable reference
    
    @crochet.run_in_reactor
    def run_spider():
        """Run the scraper spider in the background"""
        # Create the crawler with settings
        runner = CrawlerRunner({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'DOWNLOAD_TIMEOUT': 30,  # 30 seconds timeout
            'LOG_LEVEL': 'DEBUG'
        })
        
        def crawler_results(item, response, spider):
            logger.info(f"Crawler received item for URL: {url}")
            output.append(item)
        
        def spider_closed(spider):
            logger.info(f"Spider closed: {spider.name}")
            scrape_complete[0] = True
        
        # Connect the signals properly
        dispatcher.connect(crawler_results, signal=signals.item_scraped)
        dispatcher.connect(spider_closed, signal=signals.spider_closed)
        
        # Run the spider
        deferred = runner.crawl(ContentSpider, url=url, config=config)
        return deferred
    
    # Run the spider
    run_spider()
    
    # Wait for the spider to complete (up to 30 seconds)
    start_time = time.time()
    timeout = 30  # 30 seconds timeout
    
    while not scrape_complete[0] and time.time() - start_time < timeout:
        time.sleep(0.1)  # Small sleep to prevent CPU hogging
    
    # Check if we timed out
    if not scrape_complete[0]:
        logger.error(f"Scraping timed out after {timeout} seconds for URL: {url}")
        return jsonify({
            'success': False,
            'error': f'Scraping timed out after {timeout} seconds'
        })
    
    # Check if we have results
    if not output:
        logger.error(f"No data scraped from URL: {url}")
        return jsonify({
            'success': False,
            'error': 'Failed to scrape content - no data returned'
        })
    
    logger.info(f"Successfully scraped URL: {url}")
    return jsonify({
        'success': True,
        'data': output[0]
    })

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@api_bp.route('/', methods=['GET'])
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        'name': 'Content Scraper API',
        'version': '1.0',
        'endpoints': [
            {
                'path': '/api/scrape',
                'method': 'POST',
                'description': 'Scrape clean content from a URL',
                'body': {
                    'url': 'The URL to scrape',
                    'config': {
                        'title_selector': 'CSS selector for the title element',
                        'content_selector': 'CSS selector for the main content container',
                        'paragraph_selector': 'CSS selector for paragraphs within the content',
                        'extract_metadata': 'Boolean to extract metadata from meta tags',
                        'extract_images': 'Boolean to extract images',
                        'image_selector': 'CSS selector for images to extract'
                    }
                },
                'example': {
                    'url': 'https://example.com/article',
                    'config': {
                        'title_selector': 'h1.article-title',
                        'content_selector': 'div.article-body',
                        'extract_metadata': True,
                        'extract_images': True
                    }
                }
            }
        ]
    })

@api_bp.route('/test', methods=['GET'])
def test_scraper():
    """Test endpoint to check if scraper is working"""
    import requests
    from bs4 import BeautifulSoup
    
    # Simple test to see if requests and BeautifulSoup work
    try:
        response = requests.get('https://example.com', 
                               headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        # Check if response was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title"
            paragraphs = len(soup.find_all('p'))
            
            return jsonify({
                'success': True,
                'status_code': response.status_code,
                'title': title,
                'paragraphs': paragraphs,
                'content_length': len(response.text)
            })
        else:
            return jsonify({
                'success': False,
                'status_code': response.status_code,
                'error': 'Failed to get response'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@api_bp.route('/debug', methods=['GET'])
def debug_info():
    """Endpoint to get debug info about the application"""
    import os
    import sys
    import platform
    
    # Get the last log entries if log file exists
    log_entries = []
    if os.path.exists('logs/app.log'):
        try:
            with open('logs/app.log', 'r') as f:
                log_lines = f.readlines()
                log_entries = log_lines[-50:] if len(log_lines) > 50 else log_lines
        except Exception as e:
            log_entries = [f"Error reading log file: {str(e)}"]
    
    # Get system info
    system_info = {
        'python_version': sys.version,
        'platform': platform.platform()
    }
    
    # Return debug information
    return jsonify({
        'system_info': system_info,
        'recent_logs': log_entries
    })
