# src/processing/processor.py
import re
from src.processing.clean import clean_text
from src.infra.mongo.client import MongoClientSingleton
from src.infra.vector.faiss_client import FaissClient
from src.rag.embeddings import get_embedding  # hash fallback or actual model
from bson import ObjectId
from src.rag.pipeline import get_faiss_client, chunk_text, embed_text

mongo = MongoClientSingleton().db
faiss = FaissClient()

def index_quote_item(item):
    """
    Optional: index quotes in FAISS for semantic search.
    Each quote is treated as a ParsedPage-like object.
    """
    parsed = type("ParsedPageLike", (), {})()
    parsed.main_text = item.text
    parsed.url = item.url
    parsed.title = item.author
    parsed.fetched_at = item.scraped_at
    ids = []
    client = get_faiss_client()
    chunks = chunk_text(parsed.main_text)
    for idx, chunk in enumerate(chunks):
        emb = embed_text(chunk)
        metadata = {
            "url": parsed.url,
            "title": parsed.title,
            "chunk_id": idx,
            "text": chunk,
            "fetched_at": parsed.fetched_at.isoformat(),
        }
        vid = client.upsert(emb, metadata)
        ids.append(vid)
    return ids
    
def process_quote_item(item):
    text = clean_text(item.text)
    doc = {
        "text": text,
        "author": item.author,
        "tags": item.tags,
        "url": item.url,
        "scraped_at": item.scraped_at
    }

    # Update MongoDB
    res = mongo.quotes.update_one(
        {"url": item.url, "text": text},
        {"$set": doc},
        upsert=True
    )

    # Get document _id
    if res.upserted_id:
        doc_id = res.upserted_id
    else:
        existing = mongo.quotes.find_one({"url": item.url, "text": text}, {"_id": 1})
        doc_id = existing["_id"] if existing else None

    # Compute embedding
    emb = get_embedding(text)

    # Upsert vector into FAISS
    faiss.upsert(
        embedding=emb,
        metadata={"text": text, "author": item.author},
        id=None  # optional, can auto-generate or convert ObjectId to int
    )

    return {"_id": doc_id, **doc}


def process_book_image_item(item):
    """
    Store book image info in MongoDB.
    Currently FAISS embedding is not used for images.
    """
    doc = {
        "title": item.title,
        "price": item.price,
        "image_url": item.image_url,
        "local_path": item.local_path,
        "page_url": item.page_url,
        "scraped_at": item.scraped_at
    }

    # Use update_one with $set instead of replace_one with $set to avoid errors
    mongo.book_images.update_one(
        {"image_url": item.image_url},
        {"$set": doc},
        upsert=True
    )
    return doc
