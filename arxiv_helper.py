import time
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

ARXIV_API_URL = "http://export.arxiv.org/api/query"
_LAST_CALL_TS = 0.0


def _rate_limit(min_interval_seconds: float = 3.0) -> None:
    """
    arXiv API polite usage: limit calls to ~1 request / 3 seconds.
    """
    global _LAST_CALL_TS
    now = time.time()
    elapsed = now - _LAST_CALL_TS
    if elapsed < min_interval_seconds:
        time.sleep(min_interval_seconds - elapsed)
    _LAST_CALL_TS = time.time()


def _parse_feed(xml_text: str) -> List[Dict[str, Any]]:
    """
    Parse arXiv Atom XML into a list of paper dicts.
    """
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    root = ET.fromstring(xml_text)
    entries = root.findall("atom:entry", ns)

    papers: List[Dict[str, Any]] = []
    for entry in entries:
        paper_id = entry.findtext("atom:id", default="", namespaces=ns).split("/")[-1]
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        abstract = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
        published = (entry.findtext("atom:published", default="", namespaces=ns) or "").strip()

        authors = []
        for a in entry.findall("atom:author", ns):
            name = a.findtext("atom:name", default="", namespaces=ns)
            if name:
                authors.append(name.strip())

        categories = []
        for c in entry.findall("atom:category", ns):
            term = c.attrib.get("term")
            if term:
                categories.append(term)

        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
                break

        papers.append(
            {
                "id": paper_id,
                "title": title,
                "abstract": abstract,
                "published": published,
                "authors": authors,
                "categories": categories,
                "pdf_url": pdf_url,
            }
        )
    return papers


def search_arxiv(query: str, max_results: int = 5, sort_by: str = "relevance") -> List[Dict[str, Any]]:
    """
    Search arXiv with a query string.

    Args:
        query: arXiv API search query, e.g. "all:RLHF" or "cat:cs.AI AND all:transformer"
        max_results: number of results
        sort_by: "relevance" or "lastUpdatedDate" or "submittedDate"

    Returns:
        List of paper dicts.
    """
    _rate_limit(3.0)

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": "descending",
    }
    r = requests.get(ARXIV_API_URL, params=params, timeout=25)
    r.raise_for_status()
    return _parse_feed(r.text)


def get_paper_by_id(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single paper by arXiv id. Returns None if not found.
    """
    results = search_arxiv(f"id:{arxiv_id}", max_results=1, sort_by="relevance")
    if not results:
        return None
    return results[0]