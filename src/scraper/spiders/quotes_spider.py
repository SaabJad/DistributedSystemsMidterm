# """Specialized spider for scraping quotes from quotes.toscrape.com using BeautifulSoup"""
# import scrapy
# from bs4 import BeautifulSoup


# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
    
#     def __init__(self, start_urls=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Default to quotes.toscrape.com if no URLs provided
#         if isinstance(start_urls, str):
#             self.start_urls = [u.strip() for u in start_urls.split(",") if u.strip()]
#         elif isinstance(start_urls, (list, tuple)):
#             self.start_urls = list(start_urls)
#         else:
#             # Default URLs if none provided
#             self.start_urls = [
#                 "https://quotes.toscrape.com/",
#                 "https://quotes.toscrape.com/page/1/",
#                 "https://quotes.toscrape.com/page/2/",
#             ]

#     def parse(self, response):
#         """Parse the quotes page and extract structured data using BeautifulSoup."""
#         # Parse HTML with BeautifulSoup
#         soup = BeautifulSoup(response.text, 'lxml')
        
#         # Find all quote containers
#         quote_divs = soup.find_all('div', class_='quote')
        
#         for quote_div in quote_divs:
#             # Extract quote text
#             text_elem = quote_div.find('span', class_='text')
#             text = text_elem.get_text(strip=True) if text_elem else None
            
#             # Extract author
#             author_elem = quote_div.find('small', class_='author')
#             author = author_elem.get_text(strip=True) if author_elem else None
            
#             # Extract tags
#             tag_elems = quote_div.find('div', class_='tags')
#             tags = []
#             if tag_elems:
#                 tag_links = tag_elems.find_all('a', class_='tag')
#                 tags = [link.get_text(strip=True) for link in tag_links]
            
#             # Build structured data
#             yield {
#                 "url": response.url,
#                 "status": response.status,
#                 "html": response.text,  # Store full HTML for processing
#                 "quote": {
#                     "text": text,
#                     "author": author,
#                     "tags": tags,
#                 }
#             }
        
#         # Note: Pagination would need to be handled by the caller or shim
#         # The local shim doesn't support scrapy.Request properly
        
# src/scraper/spiders/quotes_spider.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import dataclass
from typing import Iterator, Dict

@dataclass
class QuoteItem:
    text: str
    author: str
    tags: list
    url: str
    scraped_at: str = datetime.utcnow().isoformat()

class QuotesSpider:
    def __init__(self, start_url="https://quotes.toscrape.com/"):
        self.start_url = start_url

    def fetch(self, url: str) -> str:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        return res.text

    def parse_page(self, html: str, page_url: str) -> Iterator[QuoteItem]:
        soup = BeautifulSoup(html, "lxml")
        for q in soup.select(".quote"):
            text = q.select_one(".text").get_text(strip=True)
            author = q.select_one(".author").get_text(strip=True)
            tags = [t.get_text(strip=True) for t in q.select(".tags .tag")]
            yield QuoteItem(text=text, author=author, tags=tags, url=page_url)

    def next_page(self, soup: BeautifulSoup) -> str | None:
        next_a = soup.select_one("li.next a")
        if next_a:
            return requests.compat.urljoin(self.start_url, next_a['href'])
        return None

    def run(self):
        url = self.start_url
        while url:
            html = self.fetch(url)
            soup = BeautifulSoup(html, "lxml")
            for item in self.parse_page(html, url):
                # send to processor / mongodb / vector upsert
                from src.processing.processor import process_quote_item
                process_quote_item(item)
            url = self.next_page(soup)
