#!/usr/bin/env python3
"""
Launch script for MCP Server with stdio transport.
This script is designed to work with MCP Inspector and other MCP clients.
"""

import sys
import asyncio
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set environment for development
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("LOG_LEVEL", "INFO")

from mcp_server_template.stdio_server import main

if __name__ == "__main__":
    asyncio.run(main())