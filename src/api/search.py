# src/api/search.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.infra.vector.faiss_client import FaissClient
from src.rag.embeddings import get_embedding

router = APIRouter()
faiss = FaissClient()

class SearchReq(BaseModel):
    q: str
    top_k: int = 5

@router.post("/search")
def search_quotes(req: SearchReq):
    emb = get_embedding(req.q)
    results = faiss.search(emb, top_k=req.top_k)
    if results is None:
        raise HTTPException(500, "search failed")
    # results should include id, score, meta
    return {"query": req.q, "results": results}
