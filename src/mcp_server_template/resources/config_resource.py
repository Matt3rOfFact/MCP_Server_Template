"""Configuration resource for exposing server settings."""

from typing import Any, Dict
from mcp.types import Resource
import json
from ..config import settings


class ConfigResource:
    """Resource for configuration information."""
    
    async def get_config(self) -> Resource:
        """Get current configuration settings."""
        config_data = {
            "app": {
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment.value,
            },
            "server": {
                "host": settings.server.host,
                "port": settings.server.port,
                "workers": settings.server.workers,
                "debug": settings.server.debug,
            },
            "features": {
                "auth_enabled": settings.auth.enabled,
                "auth_type": settings.auth.type if settings.auth.enabled else None,
                "logging_enabled": settings.middleware.logging_enabled,
                "logging_level": settings.middleware.logging_level.value,
                "rate_limiting_enabled": settings.middleware.rate_limiting_enabled,
                "cors_enabled": settings.middleware.cors_enabled,
                "cache_enabled": settings.resources.cache_enabled,
            },
            "resources": {
                "max_file_size_mb": settings.resources.max_file_size_mb,
                "allowed_file_extensions": settings.resources.allowed_file_extensions,
                "cache_ttl_seconds": settings.resources.cache_ttl_seconds,
            },
        }
        
        # Add OAuth providers if configured
        oauth_providers = []
        if settings.github_client_id:
            oauth_providers.append("github")
        if settings.google_client_id:
            oauth_providers.append("google")
        
        if oauth_providers:
            config_data["oauth"] = {
                "providers": oauth_providers
            }
        
        return Resource(
            uri="config://settings",
            name="Server Configuration",
            description="Current server configuration settings",
            mimeType="application/json",
            text=json.dumps(config_data, indent=2)
        )