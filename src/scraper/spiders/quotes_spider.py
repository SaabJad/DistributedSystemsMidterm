"""Specialized spider for scraping quotes from quotes.toscrape.com using BeautifulSoup"""
import scrapy
from bs4 import BeautifulSoup


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    
    def __init__(self, start_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default to quotes.toscrape.com if no URLs provided
        if isinstance(start_urls, str):
            self.start_urls = [u.strip() for u in start_urls.split(",") if u.strip()]
        elif isinstance(start_urls, (list, tuple)):
            self.start_urls = list(start_urls)
        else:
            # Default URLs if none provided
            self.start_urls = [
                "https://quotes.toscrape.com/",
                "https://quotes.toscrape.com/page/1/",
                "https://quotes.toscrape.com/page/2/",
            ]

    def parse(self, response):
        """Parse the quotes page and extract structured data using BeautifulSoup."""
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find all quote containers
        quote_divs = soup.find_all('div', class_='quote')
        
        for quote_div in quote_divs:
            # Extract quote text
            text_elem = quote_div.find('span', class_='text')
            text = text_elem.get_text(strip=True) if text_elem else None
            
            # Extract author
            author_elem = quote_div.find('small', class_='author')
            author = author_elem.get_text(strip=True) if author_elem else None
            
            # Extract tags
            tag_elems = quote_div.find('div', class_='tags')
            tags = []
            if tag_elems:
                tag_links = tag_elems.find_all('a', class_='tag')
                tags = [link.get_text(strip=True) for link in tag_links]
            
            # Build structured data
            yield {
                "url": response.url,
                "status": response.status,
                "html": response.text,  # Store full HTML for processing
                "quote": {
                    "text": text,
                    "author": author,
                    "tags": tags,
                }
            }
        
        # Note: Pagination would need to be handled by the caller or shim
        # The local shim doesn't support scrapy.Request properly
        
