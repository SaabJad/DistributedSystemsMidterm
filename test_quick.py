"""Quick test without user input - for automated testing."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_all():
    """Run all basic tests without user interaction."""
    print("[Quick Test Suite]")
    print("="*60)
    
    results = []
    
    # Test 1: API
    try:
        from src.api.main import health
        result = health()
        print(f"[PASS] API Health: {result}")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] API: {e}")
        results.append(False)
    
    # Test 2: Models
    try:
        from src.common.models import RawPage, ParsedPage
        from datetime import datetime
        raw = RawPage(url="https://example.com", status=200, html="<html><body>Test</body></html>")
        parsed = ParsedPage(url="https://example.com", fetched_at=datetime.utcnow(), title="Test")
        print(f"[PASS] Models: RawPage and ParsedPage created")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Models: {e}")
        results.append(False)
    
    # Test 3: HTML Parsing
    try:
        from src.processing.clean import parse_html
        from src.common.models import RawPage
        html = "<html><head><title>Test</title></head><body><p>Hello</p></body></html>"
        raw = RawPage(url="https://example.com", status=200, html=html)
        parsed = parse_html(raw)
        print(f"[PASS] HTML Parsing: title='{parsed.title}', {len(parsed.links)} links")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] HTML Parsing: {e}")
        results.append(False)
    
    # Test 4: Embeddings
    try:
        from src.rag.embeddings import embed_text
        emb = embed_text("test", dim=1536)
        print(f"[PASS] Embeddings: {len(emb)} dimensions")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Embeddings: {e}")
        results.append(False)
    
    # Test 5: FAISS
    try:
        from src.infra.vector.faiss_client import FaissClient
        from src.rag.embeddings import embed_text
        client = FaissClient(dim=1536)
        id1 = client.upsert(embed_text("test"), {"text": "test"})
        results_search = client.search(embed_text("test"), top_k=1)
        print(f"[PASS] FAISS: upserted ID={id1}, search returned {len(results_search)} results")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] FAISS: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed!")
        return 0
    else:
        print("[FAILED] Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(test_all())

