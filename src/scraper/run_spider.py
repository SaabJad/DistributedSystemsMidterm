import asyncio
import sys
from typing import List

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.scraper.spiders.basic_spider import BasicSpider


def run(start_urls: List[str]):
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(BasicSpider, start_urls=start_urls)
    process.start()


if __name__ == "__main__":
    urls = sys.argv[1:]
    if not urls:
        print("Usage: python -m src.scraper.run_spider <url1> <url2> ...")
        sys.exit(1)
    run(urls)


