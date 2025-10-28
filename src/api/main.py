from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
import os


class HealthResponse(BaseModel):
    status: str


app = FastAPI(title="Distributed RAG Scraper API", default_response_class=ORJSONResponse)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/")
def root():
    return {"service": "rag-scraper", "env": os.getenv("ENV", "dev")}


