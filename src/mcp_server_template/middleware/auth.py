"""Authentication middleware for MCP Server."""

from typing import Optional, Dict, Any
from fastmcp import FastMCP
import logging

logger = logging.getLogger(__name__)


def setup_auth_middleware(app: FastMCP, auth_token: Optional[str] = None):
    """
    Set up authentication middleware.
    
    Args:
        app: FastMCP application instance
        auth_token: Authentication token for bearer auth
    """
    
    @app.middleware("request")
    async def auth_middleware(request: Dict[str, Any], call_next):
        """Authenticate incoming requests."""
        
        # Check for authentication header
        headers = request.get("headers", {})
        auth_header = headers.get("authorization", "")
        
        if auth_token:
            # Bearer token authentication
            if not auth_header.startswith("Bearer "):
                logger.warning(f"Missing or invalid auth header from {request.get('client')}")
                return {
                    "error": "Authentication required",
                    "status": 401
                }
            
            provided_token = auth_header.replace("Bearer ", "")
            if provided_token != auth_token:
                logger.warning(f"Invalid auth token from {request.get('client')}")
                return {
                    "error": "Invalid authentication token",
                    "status": 401
                }
        
        # Call the next middleware or handler
        response = await call_next(request)
        return response


def setup_oauth_middleware(app: FastMCP, oauth_config: Dict[str, Any]):
    """
    Set up OAuth authentication middleware.
    
    Args:
        app: FastMCP application instance
        oauth_config: OAuth configuration
    """
    
    @app.middleware("request")
    async def oauth_middleware(request: Dict[str, Any], call_next):
        """Handle OAuth authentication."""
        
        # Check for OAuth token
        headers = request.get("headers", {})
        auth_header = headers.get("authorization", "")
        
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            # Validate OAuth token
            # This would typically involve:
            # 1. Checking token signature
            # 2. Verifying token expiration
            # 3. Checking token scopes
            # For now, we'll just log it
            logger.info(f"OAuth token received: {token[:10]}...")
        
        response = await call_next(request)
        return response