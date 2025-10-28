import sys
from typing import List

from dask.distributed import Client, as_completed
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.scraper.spiders.basic_spider import BasicSpider
def run_crawl(urls: List[str]) -> None:
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(BasicSpider, start_urls=urls)
    process.start()


def chunk_list(items: List[str], num_chunks: int) -> List[List[str]]:
    if num_chunks <= 1 or len(items) <= 1:
        return [items]
    size = max(1, len(items) // num_chunks + (1 if len(items) % num_chunks else 0))
    return [items[i : i + size] for i in range(0, len(items), size)]


def run_distributed(urls: List[str], num_workers: int = 2) -> None:
    with Client(n_workers=num_workers, threads_per_worker=1, processes=True) as client:
        shards = chunk_list(urls, num_workers)
        futures = [client.submit(run_crawl, shard) for shard in shards if shard]
        for _ in as_completed(futures):
            pass
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.scraper.distributed_dask_runner <url1> <url2> ... [--workers N]")
        sys.exit(1)
    args = sys.argv[1:]
    if "--workers" in args:
        idx = args.index("--workers")
        num_workers = int(args[idx + 1]) if idx + 1 < len(args) else 2
        urls = args[:idx]
    else:
        num_workers = 2
        urls = args
    run_distributed(urls, num_workers)


