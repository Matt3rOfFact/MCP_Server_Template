"""Main entry point for the MCP Server."""

import asyncio
import logging
from typing import Any, Dict, Optional
from pathlib import Path

from fastmcp import FastMCP
from mcp.types import Resource, Tool
from pydantic import BaseModel

from .config import settings
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
from .middleware import (
    setup_logging_middleware,
    setup_auth_middleware,
    setup_rate_limiting_middleware
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.middleware.logging_level.value),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP app
app = FastMCP(
    name=settings.app_name,
    version=settings.app_version
)


# Register tools
@app.tool()
async def calculate(operation: str, a: float, b: float) -> Dict[str, Any]:
    """
    Perform mathematical calculations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
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
        path: Path to the file
    
    Returns:
        File contents
    """
    return await file_operations_tool.read_file(path)


@app.tool()
async def write_file(path: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        path: Path to the file
        content: Content to write
    
    Returns:
        Success status
    """
    return await file_operations_tool.write_file(path, content)


@app.tool()
async def scrape_url(url: str, selector: Optional[str] = None) -> Dict[str, Any]:
    """
    Scrape content from a URL.
    
    Args:
        url: URL to scrape
        selector: Optional CSS selector to extract specific content
    
    Returns:
        Scraped content
    """
    return await web_scraper_tool.scrape(url, selector)


@app.tool()
async def process_data(
    data: list,
    operation: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process data with various operations.
    
    Args:
        data: Input data list
        operation: Operation to perform (filter, map, reduce, sort)
        options: Additional options for the operation
    
    Returns:
        Processed data
    """
    return await data_processor_tool.process(data, operation, options)


# Register resources
@app.resource("config://settings")
async def get_config() -> Resource:
    """Get current configuration settings."""
    return await config_resource.get_config()


@app.resource("status://server")
async def get_status() -> Resource:
    """Get server status information."""
    return await status_resource.get_status()


@app.resource("logs://recent")
async def get_recent_logs() -> Resource:
    """Get recent log entries."""
    return await logs_resource.get_recent_logs()


# Register prompts
@app.prompt()
async def coding_assistant() -> str:
    """
    A prompt for coding assistance.
    
    Returns:
        Prompt text for coding assistance
    """
    return """You are a helpful coding assistant. You can:
    1. Read and write files
    2. Perform calculations
    3. Process data
    4. Scrape web content
    
    Please provide clear and concise code examples when appropriate."""


@app.prompt()
async def data_analyst() -> str:
    """
    A prompt for data analysis.
    
    Returns:
        Prompt text for data analysis
    """
    return """You are a data analyst assistant. You can:
    1. Process and transform data
    2. Perform calculations and statistics
    3. Read data from files
    4. Scrape data from websites
    
    Focus on providing insights and visualizations when possible."""


# Setup middleware
async def setup_middleware():
    """Setup all middleware components."""
    if settings.middleware.logging_enabled:
        setup_logging_middleware(app)
    
    if settings.auth.enabled:
        setup_auth_middleware(app, settings.auth_token)
    
    if settings.middleware.rate_limiting_enabled:
        setup_rate_limiting_middleware(
            app,
            settings.middleware.requests_per_minute
        )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Handle server startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment.value}")
    
    await setup_middleware()
    
    # Initialize any database connections or external services
    if settings.database_url:
        logger.info("Connecting to database...")
        # Add database initialization here
    
    logger.info("Server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle server shutdown."""
    logger.info("Shutting down server...")
    
    # Clean up any resources
    if settings.database_url:
        logger.info("Closing database connections...")
        # Add database cleanup here
    
    logger.info("Server shutdown complete")


def main():
    """Main entry point for the application."""
    import uvicorn
    
    # Load environment-specific configuration
    if settings.environment == "production":
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "formatter": "default",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(settings.log_dir / "server.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                },
            },
            "root": {
                "level": settings.middleware.logging_level.value,
                "handlers": ["default", "file"],
            },
        }
    else:
        log_config = None
    
    # Run the server
    uvicorn.run(
        "mcp_server_template.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        workers=settings.server.workers if not settings.server.reload else 1,
        log_config=log_config,
    )


if __name__ == "__main__":
    main()