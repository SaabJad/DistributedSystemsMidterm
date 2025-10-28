import json
import os
import signal
import sys
import time
from typing import List, Optional

from confluent_kafka import Consumer, KafkaException

from src.scraper.distributed_ray_runner import run_distributed


# Configuration
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "urls")
GROUP_ID = os.environ.get("KAFKA_GROUP", "rag-scraper-group")
BATCH_SIZE = int(os.environ.get("KAFKA_BATCH_SIZE", "10"))
BATCH_TIMEOUT_SECONDS = float(os.environ.get("KAFKA_BATCH_TIMEOUT", "5.0"))


running = True


def _signal_handler(sig, frame):
    global running
    print("Shutting down consumer...")
    running = False


def _extract_url_from_message(msg) -> Optional[str]:
    if msg is None:
        return None
    if msg.error():
        raise KafkaException(msg.error())
    val = msg.value()
    if val is None:
        return None
    try:
        # confluent_kafka returns bytes
        if isinstance(val, bytes):
            s = val.decode("utf-8")
        else:
            s = str(val)
        s = s.strip()
        if not s:
            return None
        # Try JSON object with 'url' key
        if s.startswith("{"):
            obj = json.loads(s)
            if isinstance(obj, dict) and "url" in obj:
                return obj["url"]
        # Otherwise assume it's a plain URL string
        return s
    except Exception:
        return None


def consume_loop(group_id: str = GROUP_ID, topic: str = KAFKA_TOPIC, num_workers: int = 2):
    cfg = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
    consumer = Consumer(cfg)
    consumer.subscribe([topic])

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    print(f"Listening for URLs on topic '{topic}' (bootstrap={KAFKA_BOOTSTRAP})")

    try:
        while running:
            batch_msgs = []
            batch_start = time.time()
            # Collect up to BATCH_SIZE messages or until timeout
            while len(batch_msgs) < BATCH_SIZE and (time.time() - batch_start) < BATCH_TIMEOUT_SECONDS:
                msg = consumer.poll(0.5)
                if msg is None:
                    continue
                if msg.error():
                    print("Kafka message error:", msg.error())
                    continue
                url = _extract_url_from_message(msg)
                if url:
                    batch_msgs.append((msg, url))

            if not batch_msgs:
                continue

            msgs, urls = zip(*batch_msgs)
            urls = list(urls)
            print(f"Got batch of {len(urls)} urls, submitting to Ray (workers={num_workers})")

            try:
                # Submit to runner (this will block until result returned)
                run_distributed(list(urls), num_workers=num_workers)
                # Commit offsets for the last message in each partition
                # simple commit of the consumer's current positions
                consumer.commit(asynchronous=False)
                print(f"Committed offsets for {len(urls)} messages")
            except Exception as exc:
                print("Processing failed for batch:", exc)
                # Do not commit offsets; messages will be reprocessed
                time.sleep(1)

    finally:
        consumer.close()


def local_file_mode(path: str, num_workers: int = 2):
    """Read newline-separated URLs from a file and submit them in batches."""
    if not os.path.exists(path):
        print(f"Local file not found: {path}")
        return
    with open(path, "r", encoding="utf-8") as fh:
        urls = [l.strip() for l in fh.readlines() if l.strip()]
    # Submit all URLs to runner in one go (it will shard them)
    print(f"Submitting {len(urls)} urls from local file to Ray")
    run_distributed(urls, num_workers=num_workers)


def main(argv: List[str]):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--group", default=GROUP_ID)
    parser.add_argument("--topic", default=KAFKA_TOPIC)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--local-file", help="Path to newline-separated URLs for local testing")
    args = parser.parse_args(argv)

    if args.local_file:
        local_file_mode(args.local_file, num_workers=args.workers)
    else:
        consume_loop(group_id=args.group, topic=args.topic, num_workers=args.workers)


if __name__ == "__main__":
    main(sys.argv[1:])
