# src/scraper/spiders/books_spider.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class BookImageItem:
    title: str
    price: str
    image_url: str
    local_path: str
    page_url: str
    scraped_at: str = datetime.utcnow().isoformat()

class BooksSpider:
    def __init__(self, start_url="https://books.toscrape.com/"):
        self.start_url = start_url
        self.session = requests.Session()
        self.out_dir = "data/book_images"
        os.makedirs(self.out_dir, exist_ok=True)

    def fetch(self, url):
        r = self.session.get(url, timeout=15)
        r.raise_for_status()
        return r.text

    def parse_page(self, html, page_url):
        soup = BeautifulSoup(html, "lxml")
        for article in soup.select("article.product_pod"):
            title = article.h3.a['title']
            price = article.select_one(".price_color").get_text(strip=True)
            img_rel = article.select_one("img")['src']
            image_url = urljoin(page_url, img_rel)
            # download
            local_filename = os.path.join(self.out_dir, image_url.split("/")[-1].split("?")[0])
            self.download_image(image_url, local_filename)
            yield BookImageItem(title=title, price=price, image_url=image_url, local_path=local_filename, page_url=page_url)

    def download_image(self, url, path):
        if os.path.exists(path):
            return
        r = self.session.get(url, stream=True, timeout=20)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024*8):
                f.write(chunk)

    def next_page(self, soup, page_url):
        next_a = soup.select_one("li.next a")
        if next_a:
            return urljoin(page_url, next_a['href'])
        return None

    def run(self):
        url = self.start_url
        while url:
            html = self.fetch(url)
            soup = BeautifulSoup(html, "lxml")
            for item in self.parse_page(html, url):
                from src.processing.processor import process_book_image_item
                process_book_image_item(item)
            url = self.next_page(soup, url)
