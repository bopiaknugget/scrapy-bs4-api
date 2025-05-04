@api_bp.route('/scrape', methods=['POST'])
def scrape_url():
    """Endpoint to scrape content from a URL"""
    data = request.get_json()
    
    # Validate request data
    validation_result = validate_scrape_request(data)
    if validation_result:
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
            output.append(item)
        
        def spider_closed(spider):
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
    import time
    start_time = time.time()
    timeout = 30  # 30 seconds timeout
    
    while not scrape_complete[0] and time.time() - start_time < timeout:
        time.sleep(0.1)  # Small sleep to prevent CPU hogging
    
    # Check if we timed out
    if not scrape_complete[0]:
        return jsonify({
            'success': False,
            'error': f'Scraping timed out after {timeout} seconds'
        })
    
    # Check if we have results
    if not output:
        return jsonify({
            'success': False,
            'error': 'Failed to scrape content - no data returned'
        })
    
    return jsonify({
        'success': True,
        'data': output[0]
    })
