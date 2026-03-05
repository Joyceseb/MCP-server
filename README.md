# MCP-server

This project consists on building an MCP Server acting like an academic research assistant that connects an LLM (Gemini CLI) to arXiv. It can search papers by keywords and category, fetch full paper details(including abstracts and PDF links), and compare 2-3 papers in a structured way. This reduces hallucinations because Gemini relies on real tool outputs instead of guessing. The purpose being to do a 2-hour literature review in 30 seconds. 

# Features 

--> MCP Server using "FastMCP"

--> arXiv integration via official arXiv API

--> 3 MCP tools : search_papers, get_paper_details, compare_papers. 

--> MCP Resource : arxiv:/search-history
_____________________________________________________________________

## Robustness features:

|--> Error Handling + input validation (returns JSON error messages instead of crashing + arXiv ID format, max_results bounds)

|--> Rate limiting (polite API usage by reducing repeated and unnecessary calls)

|--> In-memory cache for faster repeated calls 

|--> Works with *Gemini CLI* (can be tested with MCP Inspector)

# Grounding benefit (why MCP matters): The model stops guessing citations. Instead, it uses tool outputs (real arXiv IDs + PDFs), which reduces hallucinations and improves accuracy.

## Project Structure 

├─ server.py # MCP server (tools + resource)

├─ arxiv_helper.py # arXiv API calls + XML parsing + rate limit

├─ GEMINI.md # Project "system instructions" for Gemini CLI (Option 1)

└─ README.md

## TOOLS DESCRIPTION

| Tool / Resource | Type | Inputs | Output (summary) | Purpose |
|---|---|---|---|---|
| `search_papers` | Tool | `query` (str), `category` (str, optional), `max_results` (int, 1–25) | `{query, category, results[]}` with `id,title,authors,published,categories,pdf_url` | Search arXiv by keywords + optional category filter (fast discovery). |
| `get_paper_details` | Tool | `arxiv_id` (str, `####.#####` or `vN`) | `{source: api|cache, paper{...}}` incl. `abstract` | Fetch full metadata for a paper (deep dive). Uses cache. |
| `compare_papers` | Tool | `arxiv_ids` (list of 2–3 ids) | `{papers[], comparison{...}}` | Retrieve details for 2–3 papers + return comparison scaffold for grounded synthesis. |
| `arxiv:/search-history` | Resource | none | `[{timestamp, query, category, max_results, results_returned}, ...]` | View session search history (debug/demo/audit). |

## COMPONENTS

| Component | File / Location | Role | Why we need it | Key notes |
|---|---|---|---|---|
| MCP Server (FastMCP app) | `server.py` | Exposes project features as MCP tools/resources (`search_papers`, `get_paper_details`, `compare_papers`, `arxiv:/search-history`). | Lets Gemini CLI (or any MCP client) call functions programmatically instead of relying on model memory. | Runs in **stdio** mode; returns **JSON strings**; includes input validation + error handling. |
| arXiv API Helper | `arxiv_helper.py` | Calls the arXiv API, parses the Atom XML feed, and converts results to Python dictionaries. | Keeps `server.py` clean (business logic only) and centralizes networking + XML parsing. | Includes **rate limiting (~1 request / 3s)**; uses `requests` + `xml.etree.ElementTree`. |
| In-memory Cache | `PAPER_CACHE` (inside `server.py`) | Stores fetched paper details keyed by `arxiv_id`. | Avoids repeated API calls when the LLM asks for details/compare multiple times. | Improves speed + respects arXiv limits; resets when the server restarts. |
| Search History Store | `SEARCH_HISTORY` (inside `server.py`) | Logs each search (query, category, timestamp, results count). | Useful for debugging, demos, and transparency (show what the agent actually searched). | Exposed through `arxiv:/search-history`; resets when the server restarts. |
| Input Validation | `_validate_arxiv_id` + tool checks in `server.py` | Validates `arxiv_id` format and input bounds (e.g., `max_results`). | Prevents malformed calls from crashing the server and makes tool behavior predictable. | Returns JSON error messages instead of uncaught exceptions. |
| Gemini CLI MCP Config | `settings.json` (Gemini CLI config) | Registers the MCP server so Gemini can discover and call it. | Without this, Gemini CLI cannot see or use your MCP tools. | Use **venv python path** + **absolute paths** to avoid Windows path issues. |
| MCP Inspector (Dev UI) | CLI command: `mcp dev ...` | Local UI for testing MCP tools/resources before integration. | Helps quickly debug schema issues, connection problems, and output formats. | Used to confirm tool calls and troubleshoot path/canonicalization issues. |
