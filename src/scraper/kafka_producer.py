# src/scraper/kafka_producer.py
from kafka import KafkaProducer
import json
import os

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = os.getenv("KAFKA_URL_TOPIC", "scrape-urls")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def enqueue_url(url, meta=None):
    payload = {"url": url, "meta": meta or {}}
    producer.send(TOPIC, payload)
    producer.flush()

if __name__ == "__main__":
    # example
    enqueue_url("https://quotes.toscrape.com/")
    enqueue_url("https://books.toscrape.com/")
