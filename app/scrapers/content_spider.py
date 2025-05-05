# app/scrapers/content_spider.py
import scrapy
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import traceback

from app.scrapers.extractors import ContentExtractor

class ContentSpider(scrapy.Spider):
    """Spider for scraping content from a URL"""
    name = 'content_spider'
    
    def __init__(self, url=None, config=None, *args, **kwargs):
        super(ContentSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing spider for URL: {url}")
    
    def start_requests(self):
        """Override to add headers"""
        for url in self.start_urls:
            self.logger.info(f"Starting request for URL: {url}")
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.handle_error,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                dont_filter=True
            )
    
    def parse(self, response):
        """Parse the response using Beautiful Soup"""
        self.logger.info(f"Received response: {response.status} for URL: {response.url}")
        
        try:
            # Make sure we have content
            if not response.body:
                self.logger.error("Empty response body")
                return {
                    'url': response.url,
                    'error': 'Empty response body',
                    'content': {}
                }
            
            # Try to detect encoding correctly
            try:
                # Use Beautiful Soup to parse the response
                soup = BeautifulSoup(response.body, 'html.parser', from_encoding=response.encoding)
            except Exception as e:
                self.logger.error(f"Error parsing with encoding {response.encoding}: {str(e)}")
                # Fall back to default
                soup = BeautifulSoup(response.body, 'html.parser')
            
            # Log title to help with debugging
            title_text = soup.title.string if soup.title else "No title"
            self.logger.info(f"Parsed HTML, title: {title_text}")
            
            # Extract content based on configuration
            content = ContentExtractor.extract_content(soup, self.config)
            
            # Add URL and domain info
            parsed_url = urlparse(response.url)
            domain = parsed_url.netloc
            
            return {
                'url': response.url,
                'domain': domain,
                'content': content
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing response: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                'url': response.url,
                'error': str(e),
                'content': {}
            }
    
    def handle_error(self, failure):
        """Handle request errors"""
        self.logger.error(f"Request failed: {failure.value}")
        return {
            'url': failure.request.url,
            'error': str(failure.value),
            'content': {}
        }
