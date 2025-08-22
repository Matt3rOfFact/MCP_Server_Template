"""Logging middleware for MCP Server."""

import time
import logging
from typing import Dict, Any
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def setup_logging_middleware(app: FastMCP):
    """
    Set up logging middleware.
    
    Args:
        app: FastMCP application instance
    """
    
    @app.middleware("request")
    async def logging_middleware(request: Dict[str, Any], call_next):
        """Log all incoming requests and responses."""
        
        # Record start time
        start_time = time.time()
        
        # Extract request information
        method = request.get("method", "unknown")
        path = request.get("path", "/")
        client = request.get("client", "unknown")
        
        # Log the incoming request
        logger.info(f"Request: {method} {path} from {client}")
        
        try:
            # Call the next middleware or handler
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log the response
            status = response.get("status", 200) if isinstance(response, dict) else 200
            logger.info(
                f"Response: {method} {path} - Status: {status} - "
                f"Time: {response_time:.3f}s"
            )
            
            # Add response time to response headers if possible
            if isinstance(response, dict):
                if "headers" not in response:
                    response["headers"] = {}
                response["headers"]["X-Response-Time"] = f"{response_time:.3f}s"
            
            return response
            
        except Exception as e:
            # Log any errors
            response_time = time.time() - start_time
            logger.error(
                f"Error: {method} {path} - Error: {str(e)} - "
                f"Time: {response_time:.3f}s"
            )
            raise


def setup_request_id_middleware(app: FastMCP):
    """
    Set up request ID middleware for request tracking.
    
    Args:
        app: FastMCP application instance
    """
    import uuid
    
    @app.middleware("request")
    async def request_id_middleware(request: Dict[str, Any], call_next):
        """Add unique request ID to each request."""
        
        # Generate or extract request ID
        headers = request.get("headers", {})
        request_id = headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Add request ID to request context
        request["request_id"] = request_id
        
        # Add request ID to logger context
        logger.info(f"Request ID: {request_id}")
        
        # Call next middleware
        response = await call_next(request)
        
        # Add request ID to response headers
        if isinstance(response, dict):
            if "headers" not in response:
                response["headers"] = {}
            response["headers"]["X-Request-ID"] = request_id
        
        return response