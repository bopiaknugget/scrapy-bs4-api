# app/api/validators.py
from urllib.parse import urlparse

def validate_scrape_request(data):
    """Validate the scrape request data"""
    # Check if URL is provided
    if not data or 'url' not in data:
        return 'URL is required'
    
    # Check if URL is valid
    url = data['url']
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return 'Invalid URL format'
    except:
        return 'Invalid URL'
    
    # Validate config if provided
    if 'config' in data and not isinstance(data['config'], dict):
        return 'Config must be a JSON object'
    
    return None  # No validation errors
