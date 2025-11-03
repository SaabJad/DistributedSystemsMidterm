# import os
# from typing import Optional

# from pymongo import MongoClient

# # Configuration via environment variables
# MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
# MONGO_DB = os.environ.get("MONGO_DB", "scraper")
# PARSED_COLLECTION = os.environ.get("MONGO_PARSED_COLLECTION", "parsed_pages")
# RAW_COLLECTION = os.environ.get("MONGO_RAW_COLLECTION", "raw_pages")


# _client: Optional[MongoClient] = None


# def get_client() -> MongoClient:
# 	global _client
# 	if _client is None:
# 		_client = MongoClient(MONGO_URI)
# 	return _client


# def get_db():
# 	return get_client()[MONGO_DB]


# def get_parsed_collection():
# 	return get_db()[PARSED_COLLECTION]


# def get_raw_collection():
# 	"""Return the collection used for raw scraped pages and ensure an index.

# 	Create a unique index on `url` to help idempotency when reprocessing.
# 	"""
# 	col = get_db()[RAW_COLLECTION]
# 	# create a simple unique index on url (ignore if exists)
# 	try:
# 		col.create_index("url", unique=False)
# 	except Exception:
# 		# best effort; if index creation fails, proceed
# 		pass
# 	return col


# def insert_parsed(parsed_doc: dict) -> None:
# 	"""Insert a parsed document into the parsed collection.

# 	This is a thin wrapper around PyMongo insert_one. In production you may
# 	want to add upsert semantics, retries, or bulk inserts for efficiency.
# 	"""
# 	col = get_parsed_collection()
# 	col.insert_one(parsed_doc)


# def insert_raw(raw_doc: dict) -> None:
# 	"""Insert a raw scraped document into the raw collection.

# 	This is a thin wrapper around insert_one. In production consider upsert
# 	semantics, idempotency keys, and retries.
# 	"""
# 	col = get_raw_collection()
# 	col.insert_one(raw_doc)

# src/infra/mongo/client.py
# from typing import Optional
# from pymongo import MongoClient
# import os

# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# MONGO_DB = os.getenv("MONGO_DB", "rag_scraper")


# class Mongo:
#     def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None):
#         self.uri = uri or MONGO_URI
#         self.db_name = db_name or MONGO_DB
#         self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
#         self.db = self.client[self.db_name]
#         # Collections
#         self.raw = self.db["raw_pages"]
#         self.clean = self.db["clean_pages"]

#     def insert_raw(self, doc: dict):
#         return self.raw.insert_one(doc)

#     def get_raw(self, doc_id):
#         return self.raw.find_one({"_id": doc_id})

#     def insert_clean(self, doc: dict):
#         return self.clean.insert_one(doc)

#     def find_clean(self, filter=None, limit=50):
#         filter = filter or {}
#         return list(self.clean.find(filter).limit(limit))

#     def get_clean(self, doc_id):
#         return self.clean.find_one({"_id": doc_id})
# src/infra/mongo/client.py
from pymongo import MongoClient
import os

class MongoClientSingleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            mongo_url = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            cls._instance = client
            cls._instance.db = client.get_database(os.getenv("MONGO_DB", "scraper_db"))
        return cls._instance
