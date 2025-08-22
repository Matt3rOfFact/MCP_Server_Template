"""File operations tool for reading and writing files."""

from typing import Any, Dict, Optional
from pathlib import Path
import json
import yaml
import aiofiles
from ..config import settings


class FileOperationsTool:
    """Tool for file operations."""
    
    def __init__(self):
        """Initialize the file operations tool."""
        self.max_file_size = settings.resources.max_file_size_mb * 1024 * 1024
        self.allowed_extensions = settings.resources.allowed_file_extensions
    
    async def read_file(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Read contents of a file.
        
        Args:
            path: Path to the file
            encoding: File encoding
            
        Returns:
            Dictionary containing file contents or error
        """
        try:
            file_path = Path(path).resolve()
            
            # Security checks
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            if not file_path.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {path}"
                }
            
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                return {
                    "success": False,
                    "error": f"File too large (max {settings.resources.max_file_size_mb}MB)"
                }
            
            # Check file extension
            if self.allowed_extensions and file_path.suffix not in self.allowed_extensions:
                return {
                    "success": False,
                    "error": f"File type not allowed: {file_path.suffix}",
                    "allowed_extensions": self.allowed_extensions
                }
            
            # Read file
            async with aiofiles.open(file_path, mode='r', encoding=encoding) as f:
                content = await f.read()
            
            # Parse structured formats
            parsed_content = None
            if file_path.suffix == ".json":
                try:
                    parsed_content = json.loads(content)
                except json.JSONDecodeError:
                    pass
            elif file_path.suffix in [".yaml", ".yml"]:
                try:
                    parsed_content = yaml.safe_load(content)
                except yaml.YAMLError:
                    pass
            
            return {
                "success": True,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "content": content,
                "parsed_content": parsed_content,
                "encoding": encoding
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def write_file(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            path: Path to the file
            content: Content to write
            encoding: File encoding
            create_dirs: Create parent directories if they don't exist
            
        Returns:
            Dictionary containing success status or error
        """
        try:
            file_path = Path(path).resolve()
            
            # Check file extension
            if self.allowed_extensions and file_path.suffix not in self.allowed_extensions:
                return {
                    "success": False,
                    "error": f"File type not allowed: {file_path.suffix}",
                    "allowed_extensions": self.allowed_extensions
                }
            
            # Create parent directories if needed
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            elif not file_path.parent.exists():
                return {
                    "success": False,
                    "error": f"Parent directory does not exist: {file_path.parent}"
                }
            
            # Write file
            async with aiofiles.open(file_path, mode='w', encoding=encoding) as f:
                await f.write(content)
            
            return {
                "success": True,
                "path": str(file_path),
                "size": len(content.encode(encoding)),
                "encoding": encoding
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_directory(
        self,
        path: str,
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory
            pattern: Optional glob pattern to filter files
            recursive: Whether to list recursively
            
        Returns:
            Dictionary containing directory contents or error
        """
        try:
            dir_path = Path(path).resolve()
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {path}"
                }
            
            if not dir_path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {path}"
                }
            
            # List files
            if pattern:
                if recursive:
                    files = list(dir_path.rglob(pattern))
                else:
                    files = list(dir_path.glob(pattern))
            else:
                if recursive:
                    files = list(dir_path.rglob("*"))
                else:
                    files = list(dir_path.iterdir())
            
            # Format file information
            file_info = []
            for f in files:
                if f.is_file():
                    file_info.append({
                        "name": f.name,
                        "path": str(f),
                        "size": f.stat().st_size,
                        "is_file": True,
                        "is_dir": False
                    })
                elif f.is_dir():
                    file_info.append({
                        "name": f.name,
                        "path": str(f),
                        "is_file": False,
                        "is_dir": True
                    })
            
            return {
                "success": True,
                "path": str(dir_path),
                "count": len(file_info),
                "files": file_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }