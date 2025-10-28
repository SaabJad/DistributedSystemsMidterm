"""Minimal CrawlerProcess shim used for local development/testing.

This will perform simple HTTP GETs for each start URL and call the spider's
`parse` method with a small `Response` object. It's intentionally tiny and
does not implement Scrapy features like concurrency, middlewares, pipelines,
or request scheduling.
"""
from __future__ import annotations

import logging
from typing import Iterable, List

import requests

from . import Response

logger = logging.getLogger("scrapy_shim")


class CrawlerProcess:
    def __init__(self, settings: dict | None = None):
        self.settings = settings or {}
        self._spiders: List = []

    def crawl(self, spider_cls, start_urls: Iterable[str] | None = None, *args, **kwargs):
        # instantiate spider with start_urls so project spiders that accept it continue to work
        spider = spider_cls(start_urls=start_urls, *args, **kwargs)
        self._spiders.append(spider)

    def start(self):
        results = []
        for spider in self._spiders:
            urls = getattr(spider, "start_urls", []) or []
            for url in urls:
                try:
                    resp = requests.get(url, timeout=10)
                    shim_resp = Response(url=resp.url, status=resp.status_code, text=resp.text)
                    parsed = spider.parse(shim_resp)
                    # If parse yields items (generator or list), collect them
                    if parsed is None:
                        continue
                    if hasattr(parsed, "__iter__") and not isinstance(parsed, dict):
                        for item in parsed:
                            results.append(item)
                    else:
                        results.append(parsed)
                except Exception as exc:
                    logger.exception("Error fetching %s: %s", url, exc)
        return results


__all__ = ["CrawlerProcess"]
