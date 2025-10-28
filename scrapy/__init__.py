"""A tiny local shim of the Scrapy API used by this project.

This is NOT a replacement for Scrapy. It's a minimal implementation that
provides enough of the `scrapy.Spider`, `Response` and crawling plumbing
to run the project's simple `BasicSpider` for development or tests where
Scrapy isn't installed.

If you have Scrapy installed and prefer the real package, remove or rename
this folder so the system package is used instead.
"""
from dataclasses import dataclass
from typing import Any, Generator, Iterable


class Spider:
    """Minimal Spider base class compatible with project's spiders.

    Subclasses may override `parse(self, response)` and accept `start_urls`
    in their constructor (the project's `BasicSpider` follows this pattern).
    """

    name = "shim-spider"

    def __init__(self, start_urls: Iterable[str] | None = None, *args, **kwargs):
        if isinstance(start_urls, str):
            self.start_urls = [u.strip() for u in start_urls.split(",") if u.strip()]
        elif isinstance(start_urls, (list, tuple)):
            self.start_urls = list(start_urls)
        else:
            self.start_urls = []

    def parse(self, response: Any) -> Generator[dict, None, None]:
        """Default parse - projects usually override this."""
        return


@dataclass
class Response:
    url: str
    status: int
    text: str

    # compatibility alias expected by spiders
    @property
    def body(self) -> bytes:
        return self.text.encode("utf-8")


__all__ = ["Spider", "Response"]
