# app/scrapers/extractors.py
import re

class ContentExtractor:
    """Helper class for extracting content from HTML using Beautiful Soup"""
    
    @staticmethod
    def clean_text(text):
        """Clean text by removing extra whitespace and script/style content"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove script and style content
        text = re.sub(r'<(script|style).*?</\1>', '', text, flags=re.DOTALL)
        return text
    
    @staticmethod
    def extract_content(soup, config):
        """Extract content from soup based on configuration"""
        content = {}
        
        # Extract title
        if 'title_selector' in config:
            title_elem = soup.select_one(config['title_selector'])
            content['title'] = title_elem.get_text().strip() if title_elem else None
        else:
            # Default title extraction
            title = soup.find('h1') or soup.find('title')
            content['title'] = title.get_text().strip() if title else None
        
        # Extract main content
        if 'content_selector' in config:
            main_elem = soup.select_one(config['content_selector'])
            if main_elem:
                if 'paragraph_selector' in config:
                    paragraphs = main_elem.select(config['paragraph_selector'])
                else:
                    paragraphs = main_elem.find_all('p')
                
                content['text'] = '\n\n'.join([ContentExtractor.clean_text(p.get_text()) 
                                           for p in paragraphs if p.get_text().strip()])
            else:
                content['text'] = None
        else:
            # Default content extraction
            main_content = (soup.find('article') or 
                           soup.find('div', class_='content') or 
                           soup.find('main') or 
                           soup.find('div', id='content'))
            
            if main_content:
                paragraphs = main_content.find_all('p')
                content['text'] = '\n\n'.join([ContentExtractor.clean_text(p.get_text()) 
                                           for p in paragraphs if p.get_text().strip()])
            else:
                # Fallback to body content
                body = soup.find('body')
                if body:
                    paragraphs = body.find_all('p')
                    content['text'] = '\n\n'.join([ContentExtractor.clean_text(p.get_text()) 
                                               for p in paragraphs if p.get_text().strip()])
                else:
                    content['text'] = None
        
        # Extract metadata if requested
        if config.get('extract_metadata', False):
            content['metadata'] = {}
            
            # Extract meta tags
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                if name and meta.get('content'):
                    content['metadata'][name] = meta.get('content')
        
        # Extract images if requested
        if config.get('extract_images', False):
            content['images'] = []
            
            if 'image_selector' in config:
                images = soup.select(config['image_selector'])
            else:
                # Default to main content images
                main_elem = (soup.find('article') or 
                           soup.find('div', class_='content') or 
                           soup.find('main'))
                images = main_elem.find_all('img') if main_elem else soup.find_all('img')
            
            for img in images:
                src = img.get('src')
                if src:
                    content['images'].append({
                        'src': src,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
        
        return content