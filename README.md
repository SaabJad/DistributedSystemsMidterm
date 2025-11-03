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

---

## Full Code Explanation

This project provides a distributed web scraping framework that leverages Retrieval-Augmented Generation (RAG) principles for scalable extraction, processing, and storage of web content.

### Main Components

#### 1. **API Layer**
- **Framework:** FastAPI.
- **Purpose:** Exposes endpoints to trigger scraping, check system health, and query the vector database (Qdrant).
- **Entry Point:** `src/api/main.py` (run via Uvicorn).
- **Example:** The `/health` endpoint shows the system is live.

#### 2. **Web Scraping**
- **Framework:** Scrapy (for crawling).
- **Parallel Processing:** Ray (scales out crawling & processing).
- **How it works:** Scrapy spiders fetch web pages. Ray distributes tasks to process pages concurrently.

#### 3. **Data Processing**
- **Cleaning & Parsing:**  
  - Defined in `src/processing/clean.py`.
  - Uses BeautifulSoup with lxml to parse raw HTML, remove unwanted elements (script/style/noscript), extract title, main text, and all links.
- **Batch Processing:**  
  - Handled in `src/processing/processor.py`.
  - Functions allow batch or single-page parsing, with timing metrics.
  - Results stored in MongoDB and also indexed into Qdrant.

#### 4. **Storage**
- **MongoDB:**  
  - Stores parsed results (title, main text, links, fetched at, status).
  - Interfaced via `src/infra/mongo/client.py`.
- **Vector DB (Qdrant):**  
  - Stores vectorized representations (embeddings) of parsed content for efficient retrieval.
  - Indexed after parsing using functions in `src/rag/pipeline.py`.

#### 5. **Messaging**
- **Kafka:**  
  - Used as a distributed message queue.
  - Coordinates communication between scrapers, processors, and storage tasks.

#### 6. **Configuration & Dependencies**
- **Settings:**  
  - Environment variables loaded from `.env`.
  - `.env.example` provides a template.
- **Dependencies:**  
  - Listed in `requirements.txt` for Python packages (incl. FastAPI, Scrapy, Ray, Dask, MongoDB, Qdrant, LangChain, Kafka, etc.).
  - Managed and built using `pyproject.toml`.

#### 7. **Project Structure**
- **`src/common/models.py`:**  
  Defines Pydantic models (e.g., `RawPage`, `ParsedPage`) for strongly-typed data across the system.
- **`src/processing/clean.py`:**  
  Core HTML parsing and cleaning functionality.
- **`src/processing/processor.py`:**  
  Handles single/batch processing, timing, persistence, and indexing.
- **`src/infra/`:**  
  Modules for external service integration (MongoDB, Qdrant, Kafka, etc.).
- **`src/rag/`:**  
  Handles pipeline for RAG operations such as embedding and retrieval.

### Example Data Flow

1. **User/API triggers a scrape.**
2. **Scrapy spider fetches raw HTML** (`RawPage` object).
3. **Ray distributes raw pages** to be parsed.
4. **Parsing cleans/extracts:**  
     - Title  
     - Main text  
     - Links
5. **Store parsed result in MongoDB.**
6. **Best-effort: index content into Qdrant** for semantic retrieval via embeddings.
7. **Logs & metrics** captured for monitoring and efficiency.

### Key Technologies Used

- **FastAPI:** Fast, type-checked API.
- **Scrapy:** Robust crawling.
- **Ray/Dask:** Distributed processing for scale.
- **Kafka:** Fault-tolerant message pipeline.
- **MongoDB:** Reliable data storage.
- **Qdrant:** Fast vector retrieval for RAG workflows.
- **BeautifulSoup/lxml:** HTML parsing and cleaning.
- **Pydantic:** Data validation and serialization.
- **LangChain:** Future integration for large language model (LLM) workflows.

---

This modular and distributed design ensures that the system can efficiently scrape, clean, persist, and retrieve relevant web content at scale, ready for RAG or LLM-powered applications.
If you want to extend functionality (like custom crawling, new data sources, or improved embeddings), add new modules to the `src/` hierarchy and register your changes with the relevant entrypoints.
For detailed logic, refer to code comments and the docstrings found in each key file.
Questions? Start reading the code at the FastAPI entrypoint and follow the data flow!
