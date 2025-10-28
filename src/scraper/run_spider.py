import sys
from typing import List, Optional

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.scraper.spiders.basic_spider import BasicSpider


def run(start_urls: List[str]) -> Optional[List[dict]]:
    """Run the spider for the provided start_urls.

    Returns the collected items when using the local scraper shim (which
    returns a list from `process.start()`). When running against the real
    Scrapy package this will generally return None (Scrapy pipelines handle
    item persistence).
    """
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(BasicSpider, start_urls=start_urls)
    return process.start()


if __name__ == "__main__":
    urls = sys.argv[1:]
    if not urls:
        print("Usage: python -m src.scraper.run_spider <url1> <url2> ...")
        sys.exit(1)
    run(urls)


