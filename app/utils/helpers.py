# app/utils/helpers.py
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def is_valid_url(url):
    """Check if a URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def log_request(url, config=None):
    """Log request information"""
    logger.info(f"Processing scrape request for URL: {url}")
    if config:
        logger.debug(f"Using config: {config}")

def handle_error(error_msg):
    """Log error and return formatted error message"""
    logger.error(error_msg)
    return {"error": error_msg}