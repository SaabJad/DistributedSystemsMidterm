"""RAG pipeline: chunk parsed pages, embed chunks, and index using FAISS client."""
from typing import List
import math
import os

from src.infra.vector.faiss_client import FaissClient
from src.rag.embeddings import embed_text
from src.common.models import ParsedPage

# Configuration
FAISS_DIM = int(os.environ.get("FAISS_DIM", "1536"))
FAISS_INDEX_PATH = os.environ.get("FAISS_INDEX_PATH")
FAISS_METADATA_PATH = os.environ.get("FAISS_METADATA_PATH", "faiss_metadata.json")
FAISS_COLLECTION = os.environ.get("FAISS_COLLECTION", "parsed_index")

# Simple chunk size in characters (not tokens) for demo purposes
CHUNK_SIZE = int(os.environ.get("RAG_CHUNK_SIZE", "1000"))

# Single Faiss client instance
_faiss_client: FaissClient | None = None


def get_faiss_client() -> FaissClient:
    global _faiss_client
    if _faiss_client is None:
        _faiss_client = FaissClient(dim=FAISS_DIM, index_path=FAISS_INDEX_PATH, metadata_path=FAISS_METADATA_PATH)
    return _faiss_client


def chunk_text(text: str, size: int = CHUNK_SIZE) -> List[str]:
    if not text:
        return []
    chunks = [text[i : i + size] for i in range(0, len(text), size)]
    return chunks


def index_parsed_page(parsed: ParsedPage) -> List[int]:
    """Index a ParsedPage by chunking `main_text`, embedding each chunk and
    upserting into the FAISS client. Returns list of vector ids created.
    """
    client = get_faiss_client()
    text = parsed.main_text or ""
    chunks = chunk_text(text)
    ids = []
    for idx, chunk in enumerate(chunks):
        emb = embed_text(chunk, dim=FAISS_DIM)
        metadata = {
            "url": parsed.url,
            "title": parsed.title,
            "chunk_id": idx,
            "text": chunk[:2000],
            "fetched_at": parsed.fetched_at.isoformat(),
        }
        vid = client.upsert(emb, metadata)
        ids.append(vid)
    return ids


__all__ = ["index_parsed_page", "get_faiss_client"]
