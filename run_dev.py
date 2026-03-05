# run_dev.py
import os
import sys

# Ensure current folder is on sys.path so "import server" works
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import server as _server  # imports and registers tools/resources

# IMPORTANT: expose a FastMCP object with a standard name:
mcp = _server.mcp