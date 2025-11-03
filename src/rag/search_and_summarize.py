# src/rag/search_and_summarize.py
from src.rag.embeddings import embed_text
from src.rag.llm import summarize_with_gemini
from src.rag.pipeline import get_faiss_client  # your pipeline
from typing import List

def search_and_summarize(query: str, top_k: int = 5, summary_k: int = 3):
    faiss = get_faiss_client()
    q_emb = embed_text(query)
    results = faiss.search(q_emb, top_k=top_k)  # expects (id, score, metadata) list
    # If your faiss.search returns raw tuples, normalize to a list of metadata
    top_chunks = []
    for r in results[:summary_k]:
        # adjust depending on faiss_client.search return format
        meta = r.get("metadata") if isinstance(r, dict) else r[2]
        text = meta.get("text") if isinstance(meta, dict) else str(meta)
        top_chunks.append(text)
    summary = summarize_with_gemini(top_chunks)
    return {"query": query, "results": results, "summary": summary}
