from __future__ import annotations

import json
import re
import time
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP

from arxiv_helper import search_arxiv, get_paper_by_id

mcp = FastMCP("academic-research-assistant")

# In-memory state
SEARCH_HISTORY: List[Dict[str, Any]] = []
PAPER_CACHE: Dict[str, Dict[str, Any]] = {}

_ARXIV_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")  # e.g. 2312.11456 or 2312.11456v4


def _record_search(query: str, category: str, max_results: int, n_results: int) -> None:
    SEARCH_HISTORY.append(
        {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "category": category,
            "max_results": max_results,
            "results_returned": n_results,
        }
    )


def _validate_arxiv_id(arxiv_id: str) -> str:
    arxiv_id = arxiv_id.strip()
    if not _ARXIV_ID_RE.match(arxiv_id):
        raise ValueError(
            f"Invalid arXiv ID: '{arxiv_id}'. Expected format like '2312.11456' (optionally with v2)."
        )
    return arxiv_id


def _compact(p: Dict[str, Any]) -> Dict[str, Any]:
    """Return a compact version of a paper dict for listing/search results."""
    return {
        "id": p.get("id", ""),
        "title": p.get("title", ""),
        "authors": p.get("authors", []),
        "published": p.get("published", ""),
        "categories": p.get("categories", []),
        "pdf_url": p.get("pdf_url", ""),
    }


@mcp.tool()
def search_papers(query: str, category: str = "", max_results: int = 5) -> str:
    """
    Search arXiv for papers matching a query (optionally within a category).

    Args:
        query: keywords, e.g. "RLHF" or "transformer architectures"
        category: optional arXiv category like "cs.AI". If empty, searches all.
        max_results: number of results to return (1–25)

    Returns:
        JSON string with results list (compact metadata).
    """
    try:
        max_results = int(max_results)
        if max_results < 1 or max_results > 25:
            return json.dumps({"error": "max_results must be between 1 and 25."})

        q = query.strip()
        cat = category.strip()

        # arXiv API supports boolean queries. If category is provided, constrain search.
        arxiv_query = q
        if cat:
            arxiv_query = f"cat:{cat} AND all:{q}"

        papers = search_arxiv(arxiv_query, max_results=max_results)
        _record_search(query=q, category=cat, max_results=max_results, n_results=len(papers))

        return json.dumps({"query": q, "category": cat, "results": [_compact(p) for p in papers]})
    except Exception as e:
        return json.dumps({"error": f"search_papers failed: {type(e).__name__}: {str(e)}"})


@mcp.tool()
def get_paper_details(arxiv_id: str) -> str:
    """
    Fetch full metadata for one arXiv paper by ID.

    Args:
        arxiv_id: e.g. "2312.11456" or "2312.11456v4"

    Returns:
        JSON string containing full paper metadata (including abstract).
    """
    try:
        arxiv_id = _validate_arxiv_id(arxiv_id)

        if arxiv_id in PAPER_CACHE:
            return json.dumps({"source": "cache", "paper": PAPER_CACHE[arxiv_id]})

        paper = get_paper_by_id(arxiv_id)
        if not paper:
            return json.dumps({"error": f"No paper found for id: {arxiv_id}"})

        PAPER_CACHE[arxiv_id] = paper
        return json.dumps({"source": "api", "paper": paper})
    except Exception as e:
        return json.dumps({"error": f"get_paper_details failed: {type(e).__name__}: {str(e)}"})


@mcp.tool()
def compare_papers(arxiv_ids: List[str]) -> str:
    """
    Compare 2–3 arXiv papers and return a structured comparison scaffold.

    Args:
        arxiv_ids: list of 2 or 3 arXiv IDs

    Returns:
        JSON string with paper summaries + a comparison scaffold.
        (The LLM will use this to produce a human-friendly comparison.)
    """
    try:
        if not isinstance(arxiv_ids, list) or len(arxiv_ids) not in (2, 3):
            return json.dumps({"error": "compare_papers expects a list of 2 or 3 arXiv IDs."})

        papers = []
        for pid in arxiv_ids:
            pid = _validate_arxiv_id(pid)

            if pid in PAPER_CACHE:
                paper = PAPER_CACHE[pid]
            else:
                paper = get_paper_by_id(pid)
                if not paper:
                    return json.dumps({"error": f"No paper found for id: {pid}"})
                PAPER_CACHE[pid] = paper

            papers.append(paper)

        comparison = {
            "common_themes_hint": "Look for overlaps in categories + recurring keywords in titles/abstracts.",
            "key_dimensions_hint": [
                "Problem statement",
                "Method/approach",
                "Data/experiments",
                "Main results/claims",
                "Limitations",
            ],
        }

        return json.dumps(
            {
                "papers": [
                    {
                        "id": p.get("id", ""),
                        "title": p.get("title", ""),
                        "authors": p.get("authors", []),
                        "published": p.get("published", ""),
                        "categories": p.get("categories", []),
                        "abstract": p.get("abstract", ""),
                        "pdf_url": p.get("pdf_url", ""),
                    }
                    for p in papers
                ],
                "comparison": comparison,
            }
        )
    except Exception as e:
        return json.dumps({"error": f"compare_papers failed: {type(e).__name__}: {str(e)}"})


@mcp.resource("arxiv:/search-history")
def search_history() -> str:
    """
    Return session search history as JSON.
    Useful for debugging and demos.
    """
    return json.dumps(SEARCH_HISTORY, indent=2)


if __name__ == "__main__":
    mcp.run()