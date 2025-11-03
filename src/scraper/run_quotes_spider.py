"""Run the Quotes spider for quotes.toscrape.com"""
import sys
from typing import List, Optional

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.scraper.spiders.quotes_spider import QuotesSpider


def run(start_urls: List[str] = None) -> Optional[List[dict]]:
    """Run the Quotes spider for the provided start_urls.
    
    If no URLs provided, uses default quotes.toscrape.com pages.
    """
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(QuotesSpider, start_urls=start_urls)
    return process.start()


if __name__ == "__main__":
    urls = sys.argv[1:]
    if not urls:
        print("Running Quotes spider on quotes.toscrape.com...")
        print("Usage: python -m src.scraper.run_quotes_spider [url1] [url2] ...")
        print("If no URLs provided, will scrape default pages.")
    run(urls if urls else None)

