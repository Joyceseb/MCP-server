# MCP-server

This project consists on building an MCP Server acting like an academic research assistant that connects an LLM (Gemini CLI) to arXiv. It can search papers by keywords and category, fetch full paper details(including abstracts and PDF links), and compare 2-3 papers in a structured way. This reduces hallucinations because Gemini relies on real tool outputs instead of guessing. The purpose being to do a 2-hour literature review in 30 seconds. 

# Features 

--> MCP Server using "FastMCP"

--> arXiv integration via official arXiv API

--> 3 MCP tools : search_papers, get_paper_details, compare_papers. 

--> MCP Resource : arxiv:/search-history
_____________________________________________________________________

|--> Error Handling + input validation 

|--> Rate limiting (polite API usage)

|--> In-memory cache for faster repeated calls 

|--> Works with *Gemini CLI* (can be tested with MCP Inspector)

## Project Structure 

├─ server.py # MCP server (tools + resource)

├─ arxiv_helper.py # arXiv API calls + XML parsing + rate limit

├─ GEMINI.md # Project "system instructions" for Gemini CLI (Option 1)

└─ README.md

# Tools description 

## TOOLS DESCRIPTION

| Tool / Resource | Type | Inputs (schema) | Output | Purpose | Example call |
|---|---|---|---|---|---|
| `search_papers` | Tool | `query: str` (required), `category: str = ""` (optional), `max_results: int = 5` (1–25) | JSON string: `{ "query": ..., "category": ..., "results": [ { "id","title","authors","published","categories","pdf_url" }, ... ] }` | Search arXiv by keywords and optionally filter by category (e.g., `cs.AI`). Returns compact results for quick browsing. | `{"query":"RLHF","category":"cs.AI","max_results":3}` |
| `get_paper_details` | Tool | `arxiv_id: str` (required, format `####.#####` or `####.#####vN`) | JSON string: `{ "source": "api" \| "cache", "paper": { "id","title","abstract","published","authors","categories","pdf_url" } }` | Fetch full metadata for one paper (especially the abstract). Uses in-memory cache to reduce repeated API calls and improve speed. | `{"arxiv_id":"2312.11456v4"}` |
| `compare_papers` | Tool | `arxiv_ids: List[str]` (required, length 2–3) | JSON string: `{ "papers": [ { "id","title","authors","published","categories","abstract","pdf_url" }, ... ], "comparison": { "common_themes_hint": "...", "key_dimensions_hint": [ ... ] } }` | Retrieve details for 2–3 papers and return a structured comparison scaffold so the LLM can generate a grounded comparison. | `{"arxiv_ids":["2312.11456v4","2405.07863v3"]}` |
| `arxiv:/search-history` | Resource | none | JSON string (list of `{ "timestamp","query","category","max_results","results_returned" }`) | View session search history for debugging, audit, and demos (proves tool-using behavior). | Open resource: `arxiv:/search-history` |

