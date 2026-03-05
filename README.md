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
