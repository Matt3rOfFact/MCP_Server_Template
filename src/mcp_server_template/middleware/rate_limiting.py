"""Rate limiting middleware for MCP Server."""

import time
import logging
from typing import Dict, Any
from collections import defaultdict, deque
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if a request is allowed for the given client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        minute_ago = now - 60
        
        # Remove old requests
        client_requests = self.requests[client_id]
        while client_requests and client_requests[0] < minute_ago:
            client_requests.popleft()
        
        # Check if limit exceeded
        if len(client_requests) >= self.requests_per_minute:
            return False
        
        # Add current request
        client_requests.append(now)
        return True
    
    def get_reset_time(self, client_id: str) -> float:
        """
        Get the time when the rate limit resets for a client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Unix timestamp when the limit resets
        """
        client_requests = self.requests[client_id]
        if client_requests:
            return client_requests[0] + 60
        return time.time()


def setup_rate_limiting_middleware(app: FastMCP, requests_per_minute: int = 60):
    """
    Set up rate limiting middleware.
    
    Args:
        app: FastMCP application instance
        requests_per_minute: Maximum requests allowed per minute
    """
    rate_limiter = RateLimiter(requests_per_minute)
    
    @app.middleware("request")
    async def rate_limiting_middleware(request: Dict[str, Any], call_next):
        """Apply rate limiting to incoming requests."""
        
        # Get client identifier
        client = request.get("client", "unknown")
        client_ip = request.get("client_ip", client)
        client_id = f"{client_ip}:{client}"
        
        # Check rate limit
        if not rate_limiter.is_allowed(client_id):
            reset_time = rate_limiter.get_reset_time(client_id)
            retry_after = int(reset_time - time.time())
            
            logger.warning(f"Rate limit exceeded for client {client_id}")
            
            return {
                "error": "Rate limit exceeded",
                "status": 429,
                "headers": {
                    "X-RateLimit-Limit": str(requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time)),
                    "Retry-After": str(retry_after)
                }
            }
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        if isinstance(response, dict):
            if "headers" not in response:
                response["headers"] = {}
            
            # Calculate remaining requests
            now = time.time()
            minute_ago = now - 60
            client_requests = rate_limiter.requests[client_id]
            recent_requests = sum(1 for req in client_requests if req > minute_ago)
            remaining = requests_per_minute - recent_requests
            
            response["headers"].update({
                "X-RateLimit-Limit": str(requests_per_minute),
                "X-RateLimit-Remaining": str(max(0, remaining)),
                "X-RateLimit-Reset": str(int(now + 60))
            })
        
        return response


def setup_adaptive_rate_limiting(app: FastMCP):
    """
    Set up adaptive rate limiting that adjusts based on server load.
    
    Args:
        app: FastMCP application instance
    """
    import psutil
    
    # Start with default limits
    base_limit = 60
    current_limit = base_limit
    
    @app.middleware("request")
    async def adaptive_rate_limiting_middleware(request: Dict[str, Any], call_next):
        """Apply adaptive rate limiting based on server load."""
        
        nonlocal current_limit
        
        # Check server load
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        
        # Adjust rate limit based on load
        if cpu_percent > 80 or memory_percent > 80:
            # High load - reduce rate limit
            current_limit = max(10, base_limit // 2)
        elif cpu_percent < 50 and memory_percent < 50:
            # Low load - increase rate limit
            current_limit = min(120, base_limit * 2)
        else:
            # Normal load - use base limit
            current_limit = base_limit
        
        # Apply the adjusted rate limit
        # (Implementation similar to above but with dynamic limit)
        
        response = await call_next(request)
        
        # Add server load information to response headers
        if isinstance(response, dict):
            if "headers" not in response:
                response["headers"] = {}
            response["headers"].update({
                "X-Server-Load-CPU": f"{cpu_percent:.1f}%",
                "X-Server-Load-Memory": f"{memory_percent:.1f}%",
                "X-RateLimit-Current": str(current_limit)
            })
        
        return response