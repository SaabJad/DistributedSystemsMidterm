"""Lightweight FAISS client wrapper with an in-memory metadata store.

This wrapper tries to use the `faiss` Python bindings. If FAISS is not
available, it falls back to a simple numpy brute-force index for local demos.

Note: FAISS does not store metadata; this module keeps a parallel mapping of
vector id -> metadata in-memory and persists it to disk (JSON) if configured.
For production, prefer a vector DB that natively stores metadata (Qdrant,
Weaviate, Pinecone) or persist metadata in Mongo.
"""
from __future__ import annotations

import os
import json
import threading
from typing import List, Dict, Any, Optional

import numpy as np

try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    faiss = None
    _FAISS_AVAILABLE = False


class FaissClient:
    def __init__(self, dim: int = 1536, index_path: Optional[str] = None, metadata_path: Optional[str] = None):
        self.dim = dim
        self.index_path = index_path or os.environ.get("FAISS_INDEX_PATH")
        self.metadata_path = metadata_path or os.environ.get("FAISS_METADATA_PATH", "faiss_metadata.json")
        self._lock = threading.Lock()
        self._metastore: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

        if _FAISS_AVAILABLE:
            # Use an IndexFlatIP (inner product) with ID map so we can assign ids
            self._index = faiss.IndexFlatIP(self.dim)
            self._index = faiss.IndexIDMap(self._index)
            if self.index_path and os.path.exists(self.index_path):
                try:
                    self._index = faiss.read_index(self.index_path)
                except Exception:
                    pass
        else:
            # Fallback: store embeddings in numpy arrays and brute-force search
            self._embeddings = np.zeros((0, self.dim), dtype="float32")
            self._ids: List[int] = []

        # load metadata if exists
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    # keys are strings
                    for k, v in data.items():
                        kid = int(k)
                        self._metastore[kid] = v
                    if self._metastore:
                        self._next_id = max(self._metastore.keys()) + 1
            except Exception:
                pass

    def _persist_metadata(self):
        try:
            with open(self.metadata_path, "w", encoding="utf-8") as fh:
                json.dump({str(k): v for k, v in self._metastore.items()}, fh)
        except Exception:
            pass

    def upsert(self, embedding: List[float], metadata: Dict[str, Any], id: Optional[int] = None) -> int:
        """Upsert a single vector and metadata. Returns the assigned id."""
        with self._lock:
            if id is None:
                id = self._next_id
                self._next_id += 1

            vec = np.asarray(embedding, dtype="float32")
            if vec.shape[0] != self.dim:
                # Try to pad or trim
                v = np.zeros(self.dim, dtype="float32")
                v[: min(self.dim, vec.shape[0])] = vec[: min(self.dim, vec.shape[0])]
                vec = v

            if _FAISS_AVAILABLE:
                try:
                    self._index.remove_ids(np.array([id], dtype="int64"))
                except Exception:
                    pass
                # faiss expects 2D
                self._index.add_with_ids(vec.reshape(1, -1), np.array([id], dtype="int64"))
            else:
                # fallback append
                if getattr(self, "_embeddings", None) is None:
                    self._embeddings = vec.reshape(1, -1)
                    self._ids = [id]
                else:
                    self._embeddings = np.vstack([self._embeddings, vec.reshape(1, -1)])
                    self._ids.append(id)

            self._metastore[id] = metadata
            # persist metadata best-effort
            self._persist_metadata()
            return id

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Return top_k results as list of {id, score, metadata}.

        Scores are inner-product similarities (higher = better).
        """
        vec = np.asarray(query_embedding, dtype="float32")
        if vec.shape[0] != self.dim:
            v = np.zeros(self.dim, dtype="float32")
            v[: min(self.dim, vec.shape[0])] = vec[: min(self.dim, vec.shape[0])]
            vec = v

        if _FAISS_AVAILABLE:
            D, I = self._index.search(vec.reshape(1, -1), top_k)
            ids = I[0].tolist()
            scores = D[0].tolist()
        else:
            if getattr(self, "_embeddings", None) is None or self._embeddings.shape[0] == 0:
                return []
            # inner product
            scores = (self._embeddings @ vec).tolist()
            ids = self._ids
            paired = list(zip(ids, scores))
            paired.sort(key=lambda x: x[1], reverse=True)
            paired = paired[:top_k]
            ids = [p[0] for p in paired]
            scores = [p[1] for p in paired]

        results = []
        for _id, score in zip(ids, scores):
            if _id == -1:
                continue
            md = self._metastore.get(int(_id), {})
            results.append({"id": int(_id), "score": float(score), "metadata": md})
        return results


__all__ = ["FaissClient"]
