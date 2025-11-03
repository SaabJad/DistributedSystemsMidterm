"""Test the Quotes scraper on quotes.toscrape.com"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_quotes_scraper():
    """Test scraping quotes from quotes.toscrape.com"""
    print("\n[Testing Quotes Scraper]")
    print("="*60)
    print("Target: https://quotes.toscrape.com/")
    print("="*60)
    
    try:
        # Import the scraper
        from src.scraper.run_quotes_spider import run
        
        # Run scraper on quotes.toscrape.com
        urls = ["https://quotes.toscrape.com/"]
        print(f"Running scraper on: {urls}")
        
        results = run(urls)
        
        if results:
            print(f"\n[OK] Scraper completed successfully!")
            print(f"    Scraped {len(results)} pages")
            
            # Show first few results
            if results and len(results) > 0:
                print("\n--- First Result ---")
                result = results[0]
                print(f"URL: {result.get('url')}")
                print(f"Status: {result.get('status')}")
                
                # Check if it's a quotes result with structured data
                if 'quote' in result:
                    quote_data = result['quote']
                    print("\n[Structured Quote Data:]")
                    print(f"  Text: {quote_data.get('text', 'N/A')}")
                    print(f"  Author: {quote_data.get('author', 'N/A')}")
                    print(f"  Tags: {quote_data.get('tags', [])}")
                
                # Show metadata
                print(f"\nHTML Length: {len(result.get('html', ''))} characters")
            
            return True
        else:
            print("[WARNING] No results returned from scraper")
            return False
            
    except Exception as e:
        print(f"[ERROR] Quotes scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_processing_pipeline():
    """Test the full processing pipeline with scraped quotes"""
    print("\n[Testing Full Processing Pipeline]")
    print("="*60)
    
    try:
        from src.common.models import RawPage, ParsedPage
        from src.processing.clean import parse_html
        from src.rag.embeddings import embed_text
        from src.infra.vector.faiss_client import FaissClient
        from datetime import datetime
        
        # Simulate a scraped page from quotes.toscrape.com
        sample_html = """
        <html>
            <head><title>Quotes to Scrape</title></head>
            <body>
                <div class="quote">
                    <span class="text">"The world as we have created it..."</span>
                    <span>by <small class="author">Albert Einstein</small></span>
                    <div class="tags">
                        <a class="tag">change</a>
                        <a class="tag">deep-thoughts</a>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Create RawPage
        raw = RawPage(
            url="https://quotes.toscrape.com/",
            status=200,
            html=sample_html
        )
        print("[OK] Created RawPage")
        
        # Parse HTML
        parsed = parse_html(raw)
        print(f"[OK] Parsed HTML - Title: {parsed.title}")
        print(f"[OK] Extracted {len(parsed.links)} links")
        
        # Create embedding
        text_to_embed = parsed.main_text or "test quote"
        embedding = embed_text(text_to_embed[:500])  # Limit text length
        print(f"[OK] Generated embedding: {len(embedding)} dimensions")
        
        # Store in FAISS
        client = FaissClient(dim=1536)
        metadata = {
            "url": parsed.url,
            "title": parsed.title,
            "text": text_to_embed[:200],
            "source": "quotes.toscrape.com"
        }
        vector_id = client.upsert(embedding, metadata)
        print(f"[OK] Stored in FAISS with ID: {vector_id}")
        
        # Search
        query = "Einstein quote"
        results = client.search(embed_text(query), top_k=1)
        print(f"[OK] Search for '{query}' returned {len(results)} results")
        
        if results:
            print(f"    Best match: ID {results[0]['id']}, score: {results[0]['score']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Processing pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n[Quotes Scraper Test Suite]")
    
    results = []
    
    # Test 1: Quotes scraper
    results.append(("Quotes Scraper", test_quotes_scraper()))
    
    # Test 2: Processing pipeline
    results.append(("Processing Pipeline", test_processing_pipeline()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARNING] Some tests failed")
    
    return passed == total
def test_quotes_spider_runs(tmp_path):
    spider = QuotesSpider(start_url="https://quotes.toscrape.com/")
    count = 0
    for item in spider.parse_page(spider.fetch(spider.start_url), spider.start_url):
        assert item.text
        assert item.author
        count += 1
        if count >= 3:
            break
    assert count >= 1
def test_book_images_spider_runs(tmp_path):
    spider = BooksSpider(start_url="https://books.toscrape.com/")
    count = 0
    for item in spider.parse_page(spider.fetch(spider.start_url), spider.start_url):
        assert item.title
        assert item.price
        assert item.image_url
        count += 1
        if count >= 3:
            break
    assert count >= 1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

