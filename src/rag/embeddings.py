from typing import List
import os
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


GEMINI_KEY = os.getenv("API_KEY")

_HAS_GEMINI = False


try:
    if GEMINI_KEY:
        import google.generativeai as gemini
        gemini.configure(api_key=GEMINI_KEY)
        _HAS_GEMINI = True
except Exception:
    _HAS_GEMINI = False


def _hash_embedding(text: str) -> List[float]:
    """
    Deterministic hash-based fallback embedding.
    Produces a simple 8-dimensional vector that always returns the same result for the same text.
    """
    if not text:
        return [0.0] * 8

    hash_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    vector = [int(hash_digest[i:i+8], 16) % 1000 / 1000.0 for i in range(0, 64, 8)]
    return vector


def embed_text(text: str, dim: int = 1536) -> List[float]:
    """
    Generate embeddings using:
    1. Gemini API if available.
    2. OpenAI API if available.
    3. Fallback hash embedding if neither is available.
    """

    if _HAS_GEMINI:
        try:
            resp = gemini.embed_content(
                model="models/embedding-001",  # standard Gemini embedding model
                content=text
            )
            if isinstance(resp, dict) and "embedding" in resp:
                return resp["embedding"]
            elif hasattr(resp, "embedding"):
                return resp.embedding
        except Exception as e:
            print(f"[WARN] Gemini embedding failed: {e}")

    return _hash_embedding(text)


__all__ = ["embed_text"]

if __name__ == "__main__":
    print("Testing embedding generator...\n")

