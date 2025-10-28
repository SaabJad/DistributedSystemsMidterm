import os
from typing import Any, Dict
from confluent_kafka import Producer, Consumer, KafkaException


def create_producer() -> Producer:
    cfg: Dict[str, Any] = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        "client.id": "rag-scraper-producer",
    }
    return Producer(cfg)


def create_consumer(group_id: str) -> Consumer:
    cfg: Dict[str, Any] = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    }
    return Consumer(cfg)


