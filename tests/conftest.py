"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from pathlib import Path
import tempfile
import shutil

from fastmcp import FastMCP
from mcp_server_template.config import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    settings = Settings(
        environment="development",
        app_name="Test MCP Server",
        app_version="0.0.1",
        auth_token="test-token-12345",
    )
    return settings


@pytest.fixture
async def test_app(test_settings) -> AsyncGenerator[FastMCP, None]:
    """Create a test FastMCP app."""
    app = FastMCP(
        name=test_settings.app_name,
        version=test_settings.app_version
    )
    
    # Add a simple test tool
    @app.tool()
    async def test_tool(input: str) -> dict:
        return {"result": f"Processed: {input}"}
    
    yield app


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Create a mock HTTP client."""
    client = AsyncMock()
    response = Mock()
    response.status_code = 200
    response.text = "<html><body>Test Content</body></html>"
    response.json.return_value = {"test": "data"}
    client.get.return_value = response
    return client


@pytest.fixture
def sample_data() -> list:
    """Provide sample data for testing."""
    return [
        {"id": 1, "name": "Alice", "age": 30, "score": 85},
        {"id": 2, "name": "Bob", "age": 25, "score": 92},
        {"id": 3, "name": "Charlie", "age": 35, "score": 78},
        {"id": 4, "name": "Diana", "age": 28, "score": 95},
        {"id": 5, "name": "Eve", "age": 32, "score": 88},
    ]


@pytest.fixture
def auth_headers() -> dict:
    """Provide authentication headers."""
    return {
        "authorization": "Bearer test-token-12345"
    }


@pytest.fixture
def mock_request() -> dict:
    """Create a mock request object."""
    return {
        "method": "POST",
        "path": "/test",
        "headers": {},
        "client": "test-client",
        "client_ip": "127.0.0.1",
    }