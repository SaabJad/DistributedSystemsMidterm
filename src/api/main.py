from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
import os
from .search import router as search_router
from src.infra.mongo.client import MongoClientSingleton
from fastapi import FastAPI, Query
from src.rag.pipeline import get_faiss_client
from typing import Optional
from src.rag.search_and_summarize import search_and_summarize
from src.rag.pipeline import get_faiss_client
from src.rag.embeddings import embed_text
from prometheus_client import Counter, start_http_server
REQUESTS = Counter("api_requests_total", "Total API requests", ["path", "method", "status"])
start_http_server(8002)

app = FastAPI()
mongo = MongoClientSingleton().db
faiss_client = get_faiss_client()
app.include_router(search_router, prefix="/api")


class HealthResponse(BaseModel):
    status: str


app = FastAPI(title="Distributed RAG Scraper API", default_response_class=ORJSONResponse)

@app.get("/search/quotes")
def search_quotes(query: str, top_k: int = Query(5, le=50)):
    """Semantic search over quotes using FAISS embeddings."""
    results = faiss_client.search(query, top_k=top_k)
    # results = list of dicts with metadata + similarity score
    return results

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/")
def root():
    return {"service": "rag-scraper", "env": os.getenv("ENV", "dev")}


# Raw data endpoints with pagination
@app.get("/quotes")
def get_quotes(limit: int = 20, skip: int = 0, author: Optional[str] = None, tag: Optional[str] = None):
    q = {}
    if author:
        q["author"] = author
    if tag:
        q["tags"] = tag
    cursor = mongo.quotes.find(q).sort("scraped_at", -1).skip(skip).limit(limit)
    docs = []
    for d in cursor:
        d["_id"] = str(d["_id"])
        docs.append(d)
    return {"count": len(docs), "items": docs}

@app.get("/books")
def get_books(limit: int = 20, skip: int = 0, title: Optional[str] = None):
    q = {}
    if title:
        q["title"] = {"$regex": title, "$options": "i"}
    cursor = mongo.book_images.find(q).sort("scraped_at", -1).skip(skip).limit(limit)
    docs = []
    for d in cursor:
        d["_id"] = str(d["_id"])
        docs.append(d)
    return {"count": len(docs), "items": docs}

# Semantic search (quotes)
@app.get("/search/quotes")
def api_search_quotes(query: str, top_k: int = Query(5, ge=1, le=50), summary_k: int = Query(3, ge=1, le=10)):
    try:
        return search_and_summarize(query, top_k=top_k, summary_k=summary_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
