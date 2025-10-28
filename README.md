# Distributed RAG-Based Web Scraper Framework

A distributed Retrieval-Augmented Generation (RAG) web scraping framework with Scrapy, Ray, Kafka, MongoDB, Qdrant, and FastAPI.

## Quickstart

1) Create env file

```bash
copy .env.example .env
```

2) Start infra

```bash
docker compose up -d
```

3) Run API

```bash
DistributedSystemsMidterm\venv\Scripts\python -m pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/health

## Services
- API: FastAPI
- Scraper: Scrapy + Ray
- Messaging: Kafka
- DB: MongoDB
- Vector DB: Qdrant

## Development
- Python 3.10+
- Windows PowerShell or bash
