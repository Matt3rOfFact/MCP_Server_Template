"""Resources module for MCP Server."""

from .config_resource import ConfigResource
from .status_resource import StatusResource
from .logs_resource import LogsResource

# Initialize resource instances
config_resource = ConfigResource()
status_resource = StatusResource()
logs_resource = LogsResource()

__all__ = [
    "config_resource",
    "status_resource",
    "logs_resource",
    "ConfigResource",
    "StatusResource",
    "LogsResource",
]