from time import perf_counter
from typing import Iterable, List, Dict, Any

from src.common.models import RawPage, ParsedPage
from src.processing.clean import parse_html
from src.infra.mongo.client import insert_parsed
from src.rag.pipeline import index_parsed_page


def process_and_store(raw: RawPage) -> ParsedPage:
    """Parse a RawPage and persist the ParsedPage into MongoDB.

    Returns the ParsedPage object for immediate use.
    """
    parsed: ParsedPage = parse_html(raw)
    # Convert Pydantic model to plain dict for storage
    doc = parsed.dict()
    insert_parsed(doc)
    try:
        # Index parsed page into vector store (best-effort)
        index_parsed_page(parsed)
    except Exception:
        # don't let indexing failures break processing flow
        pass
    return parsed

def process_batch(raws: Iterable[RawPage]) -> List[ParsedPage]:
    """Process a batch of RawPage objects and store each parsed result.

    Returns the list of ParsedPage objects.
    """
    return [process_and_store(r) for r in raws]


def process_batch_with_timing(raws: Iterable[RawPage]) -> Dict[str, Any]:
    """Process a batch and return timing metrics and parsed results summary.

    Returns a dictionary with keys: `count`, `elapsed_seconds`, `parsed_urls`.
    """
    start = perf_counter()
    parsed = process_batch(raws)
    elapsed = perf_counter() - start
    return {
        "count": len(parsed),
        "elapsed_seconds": elapsed,
        "parsed_urls": [p.url for p in parsed],
    }
