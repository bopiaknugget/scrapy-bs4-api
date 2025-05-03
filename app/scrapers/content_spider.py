# app/scrapers/content_spider.py
import scrapy
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from app.scrapers.extractors import ContentExtractor

class ContentSpider(scrapy.Spider):
    """Spider for scraping content from a URL"""
    name = 'content_spider'
    
    def __init__(self, url=None, config=None, *args, **kwargs):
        super(ContentSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.config = config or {}
    
    def parse(self, response):
        """Parse the response using Beautiful Soup"""
        # Use Beautiful Soup to parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
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