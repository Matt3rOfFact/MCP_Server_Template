"""Stdio-compatible MCP server for use with MCP Inspector."""

import asyncio
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from .tools import (
    calculator_tool,
    file_operations_tool,
    web_scraper_tool,
    data_processor_tool
)
from .resources import (
    config_resource,
    status_resource,
    logs_resource
)
from .config import settings


# Create FastMCP app for stdio
app = FastMCP(name=settings.app_name)


@app.tool()
async def calculate(operation: str, a: float, b: float) -> Dict[str, Any]:
    """
    Perform mathematical calculations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide, power, modulo)
        a: First number
        b: Second number
    
    Returns:
        Result of the calculation
    """
    return await calculator_tool.calculate(operation, a, b)


@app.tool()
async def read_file(path: str) -> Dict[str, Any]:
    """
    Read contents of a file.
    
    Args:
        path: Path to the file to read
    
    Returns:
        File contents and metadata
    """
    return await file_operations_tool.read_file(path)


@app.tool()
async def write_file(path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        path: Path to the file to write
        content: Content to write to the file
        create_dirs: Whether to create parent directories if they don't exist
    
    Returns:
        Success status and file information
    """
    return await file_operations_tool.write_file(path, content, create_dirs=create_dirs)


@app.tool()
async def list_directory(path: str, pattern: Optional[str] = None, recursive: bool = False) -> Dict[str, Any]:
    """
    List contents of a directory.
    
    Args:
        path: Path to the directory
        pattern: Optional glob pattern to filter files
        recursive: Whether to list files recursively
    
    Returns:
        Directory contents
    """
    return await file_operations_tool.list_directory(path, pattern, recursive)


@app.tool()
async def scrape_url(url: str, selector: Optional[str] = None, extract_links: bool = False) -> Dict[str, Any]:
    """
    Scrape content from a URL.
    
    Args:
        url: URL to scrape
        selector: Optional CSS selector to extract specific content
        extract_links: Whether to extract all links from the page
    
    Returns:
        Scraped content and metadata
    """
    return await web_scraper_tool.scrape(url, selector, extract_links)


@app.tool()
async def process_data(data: List[Any], operation: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process data with various operations.
    
    Args:
        data: Input data list to process
        operation: Operation to perform (filter, map, reduce, sort, group, aggregate, unique, sample, statistics)
        options: Additional options for the operation
    
    Returns:
        Processed data results
    """
    return await data_processor_tool.process(data, operation, options or {})


@app.resource("config://settings")
async def get_config():
    """Get current server configuration settings."""
    return await config_resource.get_config()


@app.resource("status://server") 
async def get_status():
    """Get server status and health information."""
    return await status_resource.get_status()


@app.resource("logs://recent")
async def get_recent_logs():
    """Get recent log entries from the server."""
    return await logs_resource.get_recent_logs()


@app.prompt()
async def coding_assistant():
    """A prompt template for coding assistance tasks."""
    return """You are a helpful coding assistant with access to:

Available Tools:
- calculate: Perform mathematical calculations
- read_file/write_file: Read and write files
- list_directory: Browse directory contents  
- scrape_url: Extract content from web pages
- process_data: Transform and analyze data

Available Resources:
- config://settings: Server configuration
- status://server: Server health and metrics
- logs://recent: Recent log entries

Please provide clear, practical solutions and code examples when appropriate."""


@app.prompt()
async def data_analyst():
    """A prompt template for data analysis tasks."""
    return """You are a data analyst assistant with access to:

Data Processing Capabilities:
- Statistical analysis (mean, median, mode, etc.)
- Data filtering and transformation
- Grouping and aggregation
- Sorting and sampling

File Operations:
- Read data from files (JSON, CSV, text)
- Write processed results
- Directory browsing

Web Data:
- Scrape data from websites
- Extract structured content

Focus on providing insights, identifying patterns, and suggesting data-driven solutions."""


async def main():
    """Main entry point for stdio server."""
    await app.run_stdio_async()


def run():
    """Synchronous entry point for UV scripts."""
    asyncio.run(main())


if __name__ == "__main__":
    run()