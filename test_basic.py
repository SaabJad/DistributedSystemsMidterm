"""
Basic test script to test the distributed RAG scraper.
Tests: API health, basic scraping, processing, and embeddings.
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_api_health():
    """Test 1: FastAPI health endpoint."""
    print("\n" + "="*60)
    print("TEST 1: FastAPI Health Check")
    print("="*60)
    
    try:
        from src.api.main import app, health
        result = health()
        print(f"[OK] API Health: {result}")
        return True
    except Exception as e:
        print(f"[ERROR] API Health failed: {e}")
        return False


def test_models():
    """Test 2: Pydantic models."""
    print("\n" + "="*60)
    print("TEST 2: Pydantic Models")
    print("="*60)
    
    try:
        from src.common.models import RawPage, ParsedPage
        from datetime import datetime
        
        # Test RawPage
        raw = RawPage(url="https://example.com", status=200, html="<html><body>Test</body></html>")
        print(f"[OK] RawPage created: {raw.url}")
        
        # Test ParsedPage
        parsed = ParsedPage(
            url="https://example.com",
            fetched_at=datetime.utcnow(),
            title="Test Title",
            main_text="Some content here"
        )
        print(f"[OK] ParsedPage created: {parsed.title}")
        return True
    except Exception as e:
        print(f"[ERROR] Models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_html_parsing():
    """Test 3: HTML parsing with BeautifulSoup."""
    print("\n" + "="*60)
    print("TEST 3: HTML Parsing")
    print("="*60)
    
    try:
        from src.common.models import RawPage
        from src.processing.clean import parse_html
        
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <p>Hello world!</p>
                <a href="https://example.com">Link</a>
            </body>
        </html>
        """
        
        raw = RawPage(url="https://example.com", status=200, html=html)
        parsed = parse_html(raw)
        
        print(f"[OK] Parsed title: {parsed.title}")
        print(f"[OK] Main text length: {len(parsed.main_text)} chars")
        print(f"[OK] Found {len(parsed.links)} links")
        return True
    except Exception as e:
        print(f"[ERROR] HTML parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embeddings():
    """Test 4: Embeddings generation."""
    print("\n" + "="*60)
    print("TEST 4: Embeddings Generation")
    print("="*60)
    
    try:
        from src.rag.embeddings import embed_text
        
        text = "This is a test sentence for embedding."
        embedding = embed_text(text, dim=1536)
        
        print(f"[OK] Generated embedding with {len(embedding)} dimensions")
        print(f"   First 5 values: {embedding[:5]}")
        return True
    except Exception as e:
        print(f"[ERROR] Embeddings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_faiss_client():
    """Test 5: FAISS client operations."""
    print("\n" + "="*60)
    print("TEST 5: FAISS Client Operations")
    print("="*60)
    
    try:
        from src.infra.vector.faiss_client import FaissClient
        from src.rag.embeddings import embed_text
        
        client = FaissClient(dim=1536)
        
        # Create some test embeddings
        text1 = "Machine learning is cool"
        text2 = "AI will change the world"
        text3 = "The weather is nice today"
        
        emb1 = embed_text(text1)
        emb2 = embed_text(text2)
        emb3 = embed_text(text3)
        
        # Upsert embeddings
        id1 = client.upsert(emb1, {"text": text1, "source": "test"})
        id2 = client.upsert(emb2, {"text": text2, "source": "test"})
        id3 = client.upsert(emb3, {"text": text3, "source": "test"})
        
        print(f"[OK] Upserted 3 embeddings: IDs {id1}, {id2}, {id3}")
        
        # Search for similar content
        query_emb = embed_text("Artificial intelligence")
        results = client.search(query_emb, top_k=2)
        
        print(f"[OK] Search returned {len(results)} results")
        for r in results:
            print(f"   - ID {r['id']}: score={r['score']:.4f}, text='{r['metadata'].get('text', 'N/A')}'")
        
        return True
    except Exception as e:
        print(f"[ERROR] FAISS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scraper_integration():
    """Test 6: Full scraper integration (requires internet)."""
    print("\n" + "="*60)
    print("TEST 6: Full Scraper Integration")
    print("="*60)
    
    try:
        from src.scraper.distributed_ray_runner import run_distributed
        
        # Test with a simple URL
        test_url = "https://example.com"
        print(f"Scraping {test_url}...")
        
        results = run_distributed([test_url], num_workers=1)
        
        print(f"[OK] Scraper completed")
        print(f"   Results: {results}")
        return True
    except Exception as e:
        print(f"[WARNING] Scraper test failed (may need infra running): {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n[Starting Distributed RAG Scraper Tests]")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("API Health", test_api_health()))
    results.append(("Models", test_models()))
    results.append(("HTML Parsing", test_html_parsing()))
    results.append(("Embeddings", test_embeddings()))
    results.append(("FAISS Client", test_faiss_client()))
    
    # Ask user if they want to run scraper test (needs internet + infrastructure)
    print("\n" + "="*60)
    response = input("Run scraper integration test? (requires internet + MongoDB) [y/N]: ").strip().lower()
    if response == 'y':
        results.append(("Scraper Integration", test_scraper_integration()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed!")
    else:
        print("[WARNING] Some tests failed. Check output above.")


if __name__ == "__main__":
    main()

