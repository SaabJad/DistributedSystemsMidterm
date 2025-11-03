from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
import os
from .search import router as search_router
from src.infra.mongo.client import MongoClientSingleton
from fastapi import FastAPI, Query
from src.rag.pipeline import get_faiss_client

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

@app.get("/search/books")
def search_books(query: str, top_k: int = Query(5, le=50)):
    """Semantic search over books (title + price)"""
    results = faiss_client.search(query, top_k=top_k)
    return results
    
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/")
def root():
    return {"service": "rag-scraper", "env": os.getenv("ENV", "dev")}


@app.get("/quotes")
def get_quotes(limit: int = 10):
    """Fetch latest quotes"""
    docs = list(mongo.quotes.find().sort("scraped_at", -1).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs

@app.get("/books")
def get_books(limit: int = 10):
    """Fetch latest books"""
    docs = list(mongo.book_images.find().sort("scraped_at", -1).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs