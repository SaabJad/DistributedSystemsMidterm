# from bs4 import BeautifulSoup
# from typing import Optional

# from src.common.models import RawPage, ParsedPage


# def parse_html(raw: RawPage) -> ParsedPage:
#     soup = BeautifulSoup(raw.html, "lxml")

#     for tag in soup(["script", "style", "noscript"]):
#         tag.decompose()

#     title: Optional[str] = None
#     if soup.title and soup.title.string:
#         title = soup.title.string.strip()

#     # Extract main text
#     text = soup.get_text(separator=" ", strip=True)
#     text = " ".join(text.split())

#     # Extract links
#     links = []
#     for a in soup.find_all("a", href=True):
#         href = a.get("href")
#         if href:
#             links.append(href.strip())

#     return ParsedPage(
#         url=raw.url,
#         fetched_at=raw.fetched_at,
#         title=title,
#         main_text=text if text else None,
#         links=links,
#         metadata={"status": str(raw.status)},
#     )

# src/processing/clean.py
import re
def clean_text(s: str) -> str:
    s = s.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'")
    s = re.sub(r"\s+", " ", s).strip()
    return s

