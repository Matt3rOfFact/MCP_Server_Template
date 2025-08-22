"""Web scraper tool for extracting content from URLs."""

from typing import Any, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import json


class WebScraperTool:
    """Tool for web scraping operations."""
    
    def __init__(self):
        """Initialize the web scraper tool."""
        self.timeout = 30
        self.headers = {
            "User-Agent": "MCP-Server-Template/1.0 (compatible; FastMCP)"
        }
    
    async def scrape(
        self,
        url: str,
        selector: Optional[str] = None,
        extract_links: bool = False,
        extract_images: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
            selector: Optional CSS selector to extract specific content
            extract_links: Whether to extract all links
            extract_images: Whether to extract all images
            
        Returns:
            Dictionary containing scraped content or error
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            result = {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "title": soup.title.string if soup.title else None,
            }
            
            # Extract specific content if selector provided
            if selector:
                elements = soup.select(selector)
                result["selected_content"] = [elem.get_text(strip=True) for elem in elements]
                result["selected_count"] = len(elements)
            else:
                # Get main text content
                result["text"] = soup.get_text(separator="\n", strip=True)
            
            # Extract links if requested
            if extract_links:
                links = []
                for link in soup.find_all("a", href=True):
                    links.append({
                        "text": link.get_text(strip=True),
                        "href": link["href"]
                    })
                result["links"] = links
                result["link_count"] = len(links)
            
            # Extract images if requested
            if extract_images:
                images = []
                for img in soup.find_all("img"):
                    images.append({
                        "src": img.get("src"),
                        "alt": img.get("alt", ""),
                        "title": img.get("title", "")
                    })
                result["images"] = images
                result["image_count"] = len(images)
            
            # Extract metadata
            meta_tags = {}
            for meta in soup.find_all("meta"):
                if meta.get("name"):
                    meta_tags[meta["name"]] = meta.get("content", "")
                elif meta.get("property"):
                    meta_tags[meta["property"]] = meta.get("content", "")
            result["metadata"] = meta_tags
            
            return result
            
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error {e.response.status_code}: {e.response.text[:200]}"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def fetch_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Fetch JSON data from a URL.
        
        Args:
            url: URL to fetch
            headers: Optional additional headers
            
        Returns:
            Dictionary containing JSON data or error
        """
        try:
            request_headers = self.headers.copy()
            if headers:
                request_headers.update(headers)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=request_headers)
                response.raise_for_status()
            
            # Parse JSON
            data = response.json()
            
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "data": data
            }
            
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error {e.response.status_code}: {e.response.text[:200]}"
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }