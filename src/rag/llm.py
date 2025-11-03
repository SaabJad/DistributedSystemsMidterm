from typing import List
import os
import hashlib
import struct
from dotenv import load_dotenv
load_dotenv()
from google.generativeai import configure, GenerativeModel

api_key = os.getenv("API_KEY")
configure(api_key=api_key)
model = GenerativeModel("gemini-1.5-flash")

def summarize_with_gemini(chunks: list[str]) -> str:
    text = "\n\n".join(chunks)
    prompt = f"Summarize the following text in a coherent, informative paragraph:\n{text}"
    response = model.generate_content(prompt)
    return getattr(response, "text", str(response))


