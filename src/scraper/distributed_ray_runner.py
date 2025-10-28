import os
import sys
from typing import List, Optional
import ray

def chunk_list(items: List[str], num_chunks: int) -> List[List[str]]:
    if num_chunks <= 1 or len(items) <= 1:
        return [items]
    size = max(1, len(items) // num_chunks + (1 if len(items) % num_chunks else 0))
    return [items[i : i + size] for i in range(0, len(items), size)]
@ray.remote
def _run_crawl_remote(urls: List[str]):
    """Run Scrapy CrawlerProcess inside a Ray worker for the given shard of URLs.

    Returns a small status dict so the caller can observe completion.
    """
    # Import heavy modules inside the worker to avoid serializing them
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from src.scraper.spiders.basic_spider import BasicSpider
    from src.common.models import RawPage
    from src.infra.mongo.client import insert_raw
    from src.processing.processor import process_and_store

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(BasicSpider, start_urls=urls)

    # Run crawl; the local shim returns a list of parsed items. Real Scrapy
    # may return None because pipelines handle items. We support both.
    items = process.start()

    success = 0
    failed = 0
    errors = []

    if not items:
        # No items returned by the crawler (real Scrapy pipelines likely used).
        return {"status": "completed", "count": 0, "urls": urls}

    for it in items:
        # Expecting item to be a dict with keys: url, status, html
        try:
            # Build RawPage model (will set fetched_at automatically)
            raw = RawPage(url=it.get("url"), status=int(it.get("status", 0)), html=it.get("html", ""))
        except Exception as exc:
            failed += 1
            errors.append(f"model_error:{str(exc)}")
            continue

        # Attempt to persist raw and process; retry once on failure
        attempts = 0
        max_attempts = 2
        while attempts < max_attempts:
            try:
                insert_raw(raw.dict())
                process_and_store(raw)
                success += 1
                break
            except Exception as exc:
                attempts += 1
                if attempts >= max_attempts:
                    failed += 1
                    errors.append(str(exc))
                else:
                    # small backoff
                    import time

                    time.sleep(1)

    return {"status": "completed", "success_count": success, "failed_count": failed, "errors": errors}

def run_distributed(urls: List[str], num_workers: int = 2, ray_address: Optional[str] = None) -> List[dict]:
    """Shard `urls` into `num_workers` parts, submit each as a Ray task, and wait for completion.

    If `ray_address` is None, we'll start a local Ray instance. If provided (e.g. 'auto' or 'ray://...'),
    we'll connect to that cluster address instead.
    """
    init_kwargs = {"ignore_reinit_error": True}
    if ray_address:
        init_kwargs["address"] = ray_address

    ray.init(**init_kwargs)

    shards = chunk_list(urls, num_workers)    
    futures = [_run_crawl_remote.remote(shard) for shard in shards if shard]

    results = ray.get(futures)
    if not ray_address:
        try:
            ray.shutdown()
        except Exception:
            pass

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.scraper.distributed_dask_runner <url1> <url2> ... [--workers N] [--ray-address ADDR]")
        sys.exit(1)

    args = sys.argv[1:]
    ray_address = os.environ.get("RAY_ADDRESS")
    if "--ray-address" in args:
        idx = args.index("--ray-address")
        ray_address = args[idx + 1] if idx + 1 < len(args) else ray_address
        # remove args entries so the rest are urls
        args = args[:idx] + args[idx + 2 :]

    if "--workers" in args:
        idx = args.index("--workers")
        num_workers = int(args[idx + 1]) if idx + 1 < len(args) else 2
        urls = args[:idx]
    else:
        num_workers = 2
        urls = args

    print(f"Starting distributed run with {num_workers} workers (ray_address={ray_address}) on {len(urls)} urls")
    res = run_distributed(urls, num_workers=num_workers, ray_address=ray_address)
    print("Results:", res)


