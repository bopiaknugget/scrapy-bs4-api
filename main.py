# main.py
from app import create_app
import logging
import os
import sys

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Log to console
        logging.StreamHandler(sys.stdout),
        # Log to file
        logging.FileHandler('logs/app.log')
    ]
)

# Set Scrapy logging level
logging.getLogger('scrapy').setLevel(logging.DEBUG)
logging.getLogger('twisted').setLevel(logging.INFO)

# Get root logger
logger = logging.getLogger(__name__)
logger.info("Starting Scrapy-BeautifulSoup API application")

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
