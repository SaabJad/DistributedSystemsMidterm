BOT_NAME = "rag_scraper"

SPIDER_MODULES = ["src.scraper.spiders"]
NEWSPIDER_MODULE = "src.scraper.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_TIMEOUT = 20
CONCURRENT_REQUESTS = 16
RETRY_TIMES = 2
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
    "User-Agent": "rag-scraper/0.1",
}

