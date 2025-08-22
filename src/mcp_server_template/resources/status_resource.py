"""Status resource for server health and metrics."""

import os
import platform
import psutil
from datetime import datetime
from mcp.types import Resource
import json


class StatusResource:
    """Resource for server status information."""
    
    def __init__(self):
        """Initialize the status resource."""
        self.start_time = datetime.now()
    
    async def get_status(self) -> Resource:
        """Get server status information."""
        current_time = datetime.now()
        uptime = current_time - self.start_time
        
        # Get system information
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=0.1)
        except:
            memory_info = None
            cpu_percent = 0
        
        status_data = {
            "server": {
                "status": "healthy",
                "uptime_seconds": uptime.total_seconds(),
                "uptime_formatted": str(uptime),
                "current_time": current_time.isoformat(),
                "start_time": self.start_time.isoformat(),
            },
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": platform.python_version(),
                "processor": platform.processor(),
                "cpu_count": os.cpu_count(),
            },
            "process": {
                "pid": os.getpid(),
                "cpu_percent": cpu_percent,
                "memory_rss_mb": memory_info.rss / 1024 / 1024 if memory_info else 0,
                "memory_vms_mb": memory_info.vms / 1024 / 1024 if memory_info else 0,
            },
        }
        
        # Add overall system metrics if available
        try:
            status_data["system_metrics"] = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage("/").percent,
            }
        except:
            pass
        
        return Resource(
            uri="status://server",
            name="Server Status",
            description="Current server status and metrics",
            mimeType="application/json",
            text=json.dumps(status_data, indent=2)
        )