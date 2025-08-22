"""Example client for interacting with the MCP Server."""

import asyncio
import httpx
import json
from typing import Any, Dict, Optional


class MCPClient:
    """Simple client for MCP Server interaction."""
    
    def __init__(self, base_url: str = "http://localhost:8000", auth_token: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            auth_token: Optional authentication token
        """
        self.base_url = base_url
        self.headers = {}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            Tool response
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/tools/{tool_name}",
                json=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_resource(self, resource_uri: str) -> Dict[str, Any]:
        """
        Get a resource from the MCP server.
        
        Args:
            resource_uri: URI of the resource
            
        Returns:
            Resource data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/resources/{resource_uri}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()


async def main():
    """Example usage of the MCP Client."""
    
    # Initialize client (use auth token if configured)
    client = MCPClient(auth_token="your-secret-token-here")
    
    print("MCP Server Client Example")
    print("=" * 50)
    
    # Example 1: Calculator Tool
    print("\n1. Calculator Tool:")
    try:
        result = await client.call_tool("calculate", {
            "operation": "add",
            "a": 10,
            "b": 5
        })
        print(f"   10 + 5 = {result.get('result')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 2: File Operations
    print("\n2. File Operations:")
    try:
        # Write a file
        write_result = await client.call_tool("write_file", {
            "path": "/tmp/test.txt",
            "content": "Hello from MCP Client!"
        })
        print(f"   File written: {write_result.get('success')}")
        
        # Read the file
        read_result = await client.call_tool("read_file", {
            "path": "/tmp/test.txt"
        })
        print(f"   File content: {read_result.get('content')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 3: Web Scraper
    print("\n3. Web Scraper:")
    try:
        scrape_result = await client.call_tool("scrape_url", {
            "url": "https://example.com",
            "selector": "h1"
        })
        print(f"   Title found: {scrape_result.get('selected_content', ['N/A'])[0] if scrape_result.get('selected_content') else 'N/A'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 4: Data Processing
    print("\n4. Data Processing:")
    try:
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        stats_result = await client.call_tool("process_data", {
            "data": data,
            "operation": "statistics"
        })
        stats = stats_result.get('result', {})
        print(f"   Data: {data}")
        print(f"   Mean: {stats.get('mean')}")
        print(f"   Sum: {stats.get('sum')}")
        print(f"   Min: {stats.get('min')}")
        print(f"   Max: {stats.get('max')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 5: Get Resources
    print("\n5. Resources:")
    try:
        # Get server status
        status = await client.get_resource("status://server")
        print(f"   Server Status: {status.get('server', {}).get('status')}")
        
        # Get configuration
        config = await client.get_resource("config://settings")
        print(f"   Environment: {config.get('app', {}).get('environment')}")
        
        # Get recent logs
        logs = await client.get_resource("logs://recent")
        print(f"   Recent logs: {logs.get('returned_count')} entries")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("Example completed!")


# Advanced example with error handling and retries
class AdvancedMCPClient(MCPClient):
    """Advanced MCP client with retry logic and better error handling."""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 auth_token: Optional[str] = None,
                 max_retries: int = 3,
                 timeout: int = 30):
        """
        Initialize advanced MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            auth_token: Optional authentication token
            max_retries: Maximum number of retries
            timeout: Request timeout in seconds
        """
        super().__init__(base_url, auth_token)
        self.max_retries = max_retries
        self.timeout = timeout
    
    async def call_tool_with_retry(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool with automatic retry on failure.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            Tool response
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/tools/{tool_name}",
                        json=params,
                        headers=self.headers
                    )
                    
                    # Check for rate limiting
                    if response.status_code == 429:
                        retry_after = int(response.headers.get('Retry-After', 5))
                        print(f"Rate limited. Waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    response.raise_for_status()
                    return response.json()
                    
            except httpx.TimeoutException:
                last_error = "Request timed out"
                print(f"Attempt {attempt + 1} failed: Timeout")
            except httpx.HTTPStatusError as e:
                last_error = str(e)
                print(f"Attempt {attempt + 1} failed: {e}")
            except Exception as e:
                last_error = str(e)
                print(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Failed after {self.max_retries} attempts: {last_error}")


async def advanced_example():
    """Advanced usage example with error handling."""
    
    client = AdvancedMCPClient(auth_token="your-secret-token-here")
    
    print("\nAdvanced Client Example")
    print("=" * 50)
    
    # Batch processing example
    print("\nBatch Processing:")
    tasks = []
    for i in range(5):
        task = client.call_tool_with_retry("calculate", {
            "operation": "multiply",
            "a": i,
            "b": i
        })
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"   {i} × {i} = Error: {result}")
        else:
            print(f"   {i} × {i} = {result.get('result')}")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    # Run the basic example
    asyncio.run(main())
    
    # Uncomment to run the advanced example
    # asyncio.run(advanced_example())