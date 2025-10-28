import scrapy


class BasicSpider(scrapy.Spider):
    name = "basic"

    def __init__(self, start_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(start_urls, str):
            self.start_urls = [u.strip() for u in start_urls.split(",") if u.strip()]
        elif isinstance(start_urls, (list, tuple)):
            self.start_urls = list(start_urls)
        else:
            self.start_urls = []

    def parse(self, response):
        yield {
            "url": response.url,
            "status": response.status,
            "html": response.text,
        }


