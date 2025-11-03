# src/scraper/kafka_consumer_worker.py
import os
import json
import logging
from kafka import KafkaConsumer, KafkaProducer
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from prometheus_client import Counter, start_http_server
from src.scraper.spiders.quotes_spider import QuotesSpider
from src.scraper.spiders.books_spider import BooksSpider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scraper-worker")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = os.getenv("KAFKA_URL_TOPIC", "scrape-urls")
DLQ_TOPIC = os.getenv("KAFKA_DLQ_TOPIC", "scrape-dead-letter")
CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "scraper-group")

# Prometheus metrics
SCRAPES_SUCCEEDED = Counter("scrapes_succeeded_total", "Successful scrapes")
SCRAPES_FAILED = Counter("scrapes_failed_total", "Failed scrapes")
SCRAPES_RETRIED = Counter("scrapes_retried_total", "Retry attempts")

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP,
                         value_serializer=lambda v: json.dumps(v).encode("utf-8"))

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP,
    group_id=CONSUMER_GROUP,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    enable_auto_commit=False,  # commit only on success
    auto_offset_reset="earliest"
)

def choose_spider_for_url(url: str):
    if "quotes.toscrape.com" in url:
        return QuotesSpider(start_url=url)
    if "books.toscrape.com" in url:
        return BooksSpider(start_url=url)
    # fallback
    from src.scraper.spiders.basic_spider import BasicSpider
    return BasicSpider(start_url=url)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type(Exception))
def process_url(payload):
    url = payload["url"]
    logger.info("Processing %s", url)
    spider = choose_spider_for_url(url)
    spider.run()
    SCRAPES_SUCCEEDED.inc()

def move_to_dlq(payload, reason):
    payload["_error"] = str(reason)
    producer.send(DLQ_TOPIC, payload)
    producer.flush()

if __name__ == "__main__":
    start_http_server(8001)  # Prometheus metrics endpoint for this worker
    logger.info("Worker started, listening to %s", TOPIC)
    for msg in consumer:
        payload = msg.value
        try:
            process_url(payload)
            consumer.commit()  # commit offset only on success
        except Exception as e:
            SCRAPES_FAILED.inc()
            logger.exception("Failed to process %s", payload)
            # after retries, tenacity will re-raise; then move to DLQ
            move_to_dlq(payload, e)
            consumer.commit()
