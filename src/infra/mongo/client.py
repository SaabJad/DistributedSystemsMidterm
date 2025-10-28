import os
from typing import Optional

from pymongo import MongoClient

# Configuration via environment variables
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.environ.get("MONGO_DB", "scraper")
PARSED_COLLECTION = os.environ.get("MONGO_PARSED_COLLECTION", "parsed_pages")
RAW_COLLECTION = os.environ.get("MONGO_RAW_COLLECTION", "raw_pages")


_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
	global _client
	if _client is None:
		_client = MongoClient(MONGO_URI)
	return _client


def get_db():
	return get_client()[MONGO_DB]


def get_parsed_collection():
	return get_db()[PARSED_COLLECTION]


def get_raw_collection():
	"""Return the collection used for raw scraped pages and ensure an index.

	Create a unique index on `url` to help idempotency when reprocessing.
	"""
	col = get_db()[RAW_COLLECTION]
	# create a simple unique index on url (ignore if exists)
	try:
		col.create_index("url", unique=False)
	except Exception:
		# best effort; if index creation fails, proceed
		pass
	return col


def insert_parsed(parsed_doc: dict) -> None:
	"""Insert a parsed document into the parsed collection.

	This is a thin wrapper around PyMongo insert_one. In production you may
	want to add upsert semantics, retries, or bulk inserts for efficiency.
	"""
	col = get_parsed_collection()
	col.insert_one(parsed_doc)


def insert_raw(raw_doc: dict) -> None:
	"""Insert a raw scraped document into the raw collection.

	This is a thin wrapper around insert_one. In production consider upsert
	semantics, idempotency keys, and retries.
	"""
	col = get_raw_collection()
	col.insert_one(raw_doc)

