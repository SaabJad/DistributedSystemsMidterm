Distributed RAG Scraper – Version 2
What changed: 
✅ Implemented

Dual-site scraping (quotes + books)

Structured MongoDB storage

FAISS vector indexing

Gemini-powered summarization for retrieved results

Kafka-based distributed task queue

Unified spider runner (run_spider.py)

Comprehensive FastAPI endpoints for retrieval and search

Working tests (test_basic.py, test_quick.py, test_quotes_scraper.py)


Gemini API integration

Improved error handling and retry logic in scraper

Added load balancing between worker nodes

Fixed FAISS upsert to handle vector dimension consistency

Removed unused clients and redundant imports
/////////////////////////////////////////////////////////////////////////////////////////////////


1_Project Architecture and Structure

 Architecture Diagram
Users → Nginx/HAProxy (Load Balancer)
          ↓
      FastAPI Gateway
          ↓
 ┌────────────────────────────────────────────┐
 │          Distributed Processing Layer      │
 │────────────────────────────────────────────│
 │                                            │
 │  [Scraper Workers] ←→ [Kafka] ←→ [MongoDB] │
 │       ↑                ↓                  │
 │   (Ray/Dask)     DLQ for retries          │
 │                                            │
 │  [RAG Engine] ←→ [FAISS Vector DB]        │
 │        ↓                                   │
 │   [Gemini Generative AI Summarizer]       │
 │                                            │
 │  [Prometheus / Grafana Monitoring]         │
 └────────────────────────────────────────────┘
          ↓
      Docker / Kubernetes Cluster



DistributedSystemsMidterm/
├── src/
│   ├── api/
│   │   └── search.py
|   |   |── main.py         # FastAPI endpoints
│   ├── common/
│   │   └── models.py       # RawPage, ParsedPage Pydantic models
│   ├── infra/
│   │   ├── vector/faiss_client.py  # FAISS client for vector storage
│   │   ├── mongo/client.py         # MongoDB client
│   │   └── kafka/client.py         # Kafka client 
│   ├── processing/
│   │   ├── clean.py
│   │   └── processor.py            # Process quotes & book images
│   ├── rag/
│   │   ├── embeddings.py 
|   |   |──llm.py
|   |   |──search_and_summarize.py         
│   │   └── pipeline.py             # Chunking & indexing parsed pages
│   └── scraper/
│       ├── run_spider.py           # Unified spider runner
│       ├── run_quotes_spider.py    # Example specialized spider
│       ├── distributed_ray_runner.py
|       |──kafka_consumer_worker.py
|       |──kafka_consumer.py
|       |──kafka_producer.py
│       └── spiders/
│           ├── basic_spider.py
|           |──books_spider.py
│           └── quotes_spider.py
|── data\book_images...
├── scrapy/
│   ├── __init__.py
│   └── crawler.py
|── faiss_metadata.json
|── docker-compose.yml
|── promethius.yml
|── pyproject.toml
|── requirements.txt
│── test_basic.py
│── test_quick.py
|── test_quotes_scraper.py
└── README.md

/////////////////////////////////////////////////////////////////////////////////////////////////
Prerequisites

Python 3.10+

MongoDB (running locally or remotely)

Kafka (for distributed scraping)

FAISS (installed automatically via requirements.txt)

Gemini API Key (for LLM summaries and embeddings)
/////////////////////////////////////////////////////////////////////////////////////////////////
Setup

Create and activate a virtual environment:

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

/////////////////////////////////////////////////////////////////////////////////////////////////
Install dependencies:

pip install -r requirements.txt


Create a .env file in the project root:

MONGO_URI=mongodb://localhost:27017
FAISS_INDEX_PATH=faiss_index.bin
GEMINI_API_KEY= 


Run a local MongoDB instance (default URI: mongodb://localhost:27017/).
/////////////////////////////////////////////////////////////////////////////////////////////////
Note:
The FAISS index file will be automatically created on first run.
If Kafka is configured, tasks will be distributed among multiple worker nodes.
/////////////////////////////////////////////////////////////////////////////////////////////////
Step 1 – Run Spiders
Quotes spider (text scraping)
python -m src.scraper.run_spider quotes --start-url https://quotes.toscrape.com/

Books spider (image + metadata scraping)
python -m src.scraper.run_spider books --start-url https://books.toscrape.com/

Distributed mode (optional)

Use Kafka to balance scraping tasks between workers:

python -m src.scraper.distributed_ray_runner --topic quotes_tasks


These spiders fetch, clean, and store structured content into MongoDB and FAISS.
/////////////////////////////////////////////////////////////////////////////////////////////////
Step 2 – Run FastAPI Server

Start the API service:

uvicorn src.api.main:app --reload


Open the API docs:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc
/////////////////////////////////////////////////////////////////////////////////////////////////
Step 3 – Example API Requests
Search quotes (semantic + summarized)
curl "http://127.0.0.1:8000/search/quotes?query=inspiration&top_k=5"

Get all books
curl "http://127.0.0.1:8000/books"

Semantic book search with Gemini summaries
curl "http://127.0.0.1:8000/search/books?query=philosophy"
/////////////////////////////////////////////////////////////////////////////////////////////////
4. Architecture Overview
Scraping Layer

BasicSpider → Generic spider for unstructured pages

QuotesSpider → Specialized scraper for quotes

BooksSpider → Extracts book metadata and image URLs

Supports Kafka-based distributed crawling for large-scale workloads

Processing Layer

Cleans and normalizes text using clean.py

Stores processed data into MongoDB (quotes, books, and book_images collections)

Embeds text via src/rag/embeddings.py using Gemini Embeddings API

RAG / Vector Store Layer

FAISS client (src/infra/vector/faiss_client.py) manages local vector storage

Texts are chunked and indexed through src/rag/pipeline.py

Gemini LLM generates contextual summaries for retrieved text chunks

Enables semantic search across quotes and books

API Layer (FastAPI)

/quotes → Retrieve stored quotes

/books → Retrieve stored books

/search/quotes → FAISS-based semantic quote search

/search/books → Semantic search + Gemini contextual summaries

Includes pagination, filters, and structured JSON responses

Deployment Layer

Dockerized microservices (API, Scraper, RAG, Vector DB)

Docker Compose for local orchestration

Optional Kubernetes deployment with autoscaling

HAProxy/Nginx for API load balancing

Prometheus/Grafana for system monitoring and alerting







