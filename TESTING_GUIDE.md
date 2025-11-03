# Testing Guide for Distributed RAG Scraper

This guide provides step-by-step instructions to test your distributed RAG scraper framework.

---

## Prerequisites

### 1. Install Dependencies

```bash
# Make sure you're in the project root
cd C:\Users\saabj\OneDrive\Desktop\DistributedSystemsMidterm

# If using a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Setup Environment File

Create a `.env` file in the project root with:

```bash
ENV=dev
API_KEY=your_openai_api_key_here  # Leave empty to use hash-based fallback
MONGO_URI=mongodb://localhost:27017
MONGO_DB=scraper
FAISS_DIM=1536
```

---

## Test Levels

### Level 1: Unit Tests (No Infrastructure Required)

Run the basic unit tests that don't require Docker or external services:

```bash
python test_basic.py
```

This tests:
- ✅ API health endpoint
- ✅ Pydantic models
- ✅ HTML parsing with BeautifulSoup
- ✅ Embeddings generation (with fallback)
- ✅ FAISS client operations

**Expected output:**
```
🚀 Starting Distributed RAG Scraper Tests
============================================================
TEST 1: FastAPI Health Check
✅ API Health: status='ok'
...
```

---

### Level 2: Integration Tests (Requires Docker)

#### Step 1: Start Infrastructure

```bash
# Start all services (MongoDB, Kafka, Qdrant)
docker compose up -d

# Check services are running
docker compose ps
```

You should see:
- `rag_mongo` (MongoDB on port 27017)
- `rag_zookeeper` (Zookeeper on port 2181)
- `rag_kafka` (Kafka on port 9092)
- `rag_qdrant` (Qdrant on ports 6333, 6334)

#### Step 2: Test MongoDB Connection

```bash
python -c "from src.infra.mongo.client import get_client; print('✅ MongoDB connected:', get_client().server_info())"
```

#### Step 3: Test API Server

```bash
# In terminal 1: Start the API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# In terminal 2: Test the health endpoint
curl http://localhost:8000/health
# Or open in browser: http://localhost:8000/health
```

**Expected response:**
```json
{"status":"ok"}
```

#### Step 4: Test Full Scraping Pipeline

```bash
# Test scraping a single URL without Kafka
python -m src.scraper.distributed_ray_runner https://example.com https://example.org

# Check MongoDB for results
python -c "from src.infra.mongo.client import get_parsed_collection; print(list(get_parsed_collection().find({}, {'url':1, 'title':1}).limit(5)))"
```

---

### Level 3: End-to-End Test (Full System)

#### Test with Kafka Message Queue

```bash
# In terminal 1: Start Kafka consumer (scraper)
python -m src.scraper.kafka_consumer --workers 2

# In terminal 2: Send URLs to Kafka
python -c "
from src.infra.kafka.client import create_producer
import json

producer = create_producer()
urls = ['https://example.com', 'https://example.org']

for url in urls:
    producer.produce('urls', value=json.dumps({'url': url}))
    producer.flush()
    print(f'Sent: {url}')
"
```

**Expected output in terminal 1:**
```
Listening for URLs on topic 'urls'...
Got batch of 2 urls, submitting to Ray
Committed offsets for 2 messages
```

#### Test Vector Search

```bash
python -c "
from src.infra.vector.faiss_client import FaissClient
from src.rag.embeddings import embed_text

# Get FAISS client
client = FaissClient()

# Search for something
query = 'machine learning'
results = client.search(embed_text(query), top_k=3)
print('Search results:', results)
"
```

---

## Testing Specific Components

### Test Web Scraping

```bash
# Single URL scraping
python -m src.scraper.run_spider https://example.com

# Distributed scraping with Ray
python -m src.scraper.distributed_ray_runner https://example.com https://example.org --workers 2
```

### Test HTML Parsing

```bash
python -c "
from src.common.models import RawPage
from src.processing.clean import parse_html

html = '<html><head><title>Test</title></head><body><p>Hello</p></body></html>'
raw = RawPage(url='https://example.com', status=200, html=html)
parsed = parse_html(raw)
print('Title:', parsed.title)
print('Text:', parsed.main_text)
print('Links:', parsed.links)
"
```

### Test RAG Pipeline

```bash
python -c "
from src.rag.pipeline import get_faiss_client, chunk_text
from src.common.models import ParsedPage
from datetime import datetime

# Create a test parsed page
parsed = ParsedPage(
    url='https://example.com',
    fetched_at=datetime.utcnow(),
    title='Test Page',
    main_text='This is a long text about machine learning and AI.'
)

# Index it
from src.rag.pipeline import index_parsed_page
ids = index_parsed_page(parsed)
print('Indexed IDs:', ids)

# Search it
client = get_faiss_client()
from src.rag.embeddings import embed_text
results = client.search(embed_text('machine learning'), top_k=1)
print('Search results:', results)
"
```

---

## Debugging

### Common Issues

#### 1. MongoDB Connection Error
```
pymongo.errors.ServerSelectionTimeoutError
```
**Solution:** Make sure MongoDB is running: `docker compose up mongo -d`

#### 2. Kafka Connection Error
```
confluent_kafka.KafkaException: Broker transport failure
```
**Solution:** Make sure Kafka and Zookeeper are running: `docker compose up kafka zookeeper -d`

#### 3. Import Errors
```
ModuleNotFoundError: No module named 'src'
```
**Solution:** Make sure you're in the project root and `src` directory exists.

#### 4. FAISS Installation Issues
```
ImportError: No module named 'faiss'
```
**Solution:** Install FAISS: `pip install faiss-cpu` (or `faiss-gpu` for GPU support)

#### 5. Ray Installation Issues
```
ImportError: No module named 'ray'
```
**Solution:** Install Ray: `pip install ray`

---

## Performance Testing

### Test Distributed Processing

```bash
# Test with multiple workers
python -m src.scraper.distributed_ray_runner \
  https://example.com https://example.org https://example.net \
  --workers 4

# Measure time
python -c "
from src.processing.processor import process_batch_with_timing
from src.common.models import RawPage
import time

raws = [
    RawPage(url=f'https://example.com', status=200, html='<html><body>Test {i}</body></html>')
    for i in range(10)
]

result = process_batch_with_timing(raws)
print(f'Processed {result[\"count\"]} pages in {result[\"elapsed_seconds\"]:.2f}s')
"
```

---

## CI/CD Testing

For automated testing, create `tests/test_all.py`:

```python
import unittest
from test_basic import *

class TestAll(unittest.TestCase):
    def test_api_health(self):
        self.assertTrue(test_api_health())
    
    def test_models(self):
        self.assertTrue(test_models())
    
    def test_html_parsing(self):
        self.assertTrue(test_html_parsing())
```

Run with:
```bash
python -m pytest tests/
```

---

## Next Steps

1. ✅ Run `python test_basic.py` to verify basic functionality
2. ✅ Start infrastructure with `docker compose up -d`
3. ✅ Test API endpoint: `curl http://localhost:8000/health`
4. ✅ Test scraping: `python -m src.scraper.run_spider https://example.com`
5. ✅ Check results in MongoDB
6. ✅ Test vector search with FAISS

---

## Questions?

- Check `README.md` for full documentation
- Review code comments in `src/` modules
- Check Docker logs: `docker compose logs -f`

