from typing import List
import os
import hashlib
import struct

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("API_KEY")
import hashlib

def get_embedding(text: str):
    """
    Generate a deterministic hash-based embedding for a given text.
    This acts as a fallback when no real embedding model (like OpenAI or SentenceTransformers) is used.
    """
    if not text:
        return [0.0] * 8  # minimal dummy vector

    # Convert the SHA256 hash into a numeric embedding (8-dimensional vector)
    hash_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    vector = [int(hash_digest[i:i+8], 16) % 1000 / 1000.0 for i in range(0, 64, 8)]
    return vector
try:
    if api_key:
        import openai
        openai.api_key = api_key
        _API_AVAILABLE = True
    else:
        _API_AVAILABLE = False
except Exception:
    _API_AVAILABLE = False
def embed_text(text: str, dim: int = 1536) -> List[float]:
    if _API_AVAILABLE:
        try:
            resp = openai.Embedding.create(model="text-embedding-3-small", input=text)
            vec = resp["data"][0]["embedding"]
            # ensure length matches dim (model chosen should match)
            if len(vec) != dim:
                # pad or trim
                v = [0.0] * dim
                for i in range(min(len(vec), dim)):
                    v[i] = vec[i]
                return v
            return vec
        except Exception:
            pass

    h = hashlib.sha256(text.encode("utf-8")).digest()
    nums = []
    # expand hash into floats
    while len(nums) < dim:
        h = hashlib.sha256(h).digest()
        for i in range(0, len(h), 4):
            if len(nums) >= dim:
                break
            chunk = h[i : i + 4]
            val = struct.unpack("!I", chunk)[0]
            # map to [-1,1]
            nums.append(((val / 0xFFFFFFFF) * 2.0) - 1.0)
    return nums[:dim]
__all__ = ["embed_text"]
