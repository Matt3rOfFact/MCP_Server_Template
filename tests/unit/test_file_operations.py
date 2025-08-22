"""Unit tests for file operations tool."""

import pytest
from pathlib import Path
import json
import yaml

from mcp_server_template.tools.file_operations import FileOperationsTool
from mcp_server_template.config import Settings


@pytest.fixture
def file_tool():
    """Create a file operations tool instance."""
    settings = Settings()
    settings.resources.allowed_file_extensions = [".txt", ".json", ".yaml", ".yml"]
    settings.resources.max_file_size_mb = 10
    return FileOperationsTool()


class TestFileOperationsTool:
    """Test suite for FileOperationsTool."""
    
    @pytest.mark.asyncio
    async def test_read_text_file(self, file_tool, temp_dir):
        """Test reading a text file."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)
        
        # Read file
        result = await file_tool.read_file(str(test_file))
        
        assert result["success"] is True
        assert result["content"] == test_content
        assert result["path"] == str(test_file)
    
    @pytest.mark.asyncio
    async def test_read_json_file(self, file_tool, temp_dir):
        """Test reading and parsing a JSON file."""
        # Create test JSON file
        test_file = temp_dir / "test.json"
        test_data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(test_data))
        
        # Read file
        result = await file_tool.read_file(str(test_file))
        
        assert result["success"] is True
        assert result["parsed_content"] == test_data
    
    @pytest.mark.asyncio
    async def test_read_yaml_file(self, file_tool, temp_dir):
        """Test reading and parsing a YAML file."""
        # Create test YAML file
        test_file = temp_dir / "test.yaml"
        test_data = {"key": "value", "list": [1, 2, 3]}
        test_file.write_text(yaml.dump(test_data))
        
        # Read file
        result = await file_tool.read_file(str(test_file))
        
        assert result["success"] is True
        assert result["parsed_content"] == test_data
    
    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, file_tool):
        """Test reading a nonexistent file."""
        result = await file_tool.read_file("/nonexistent/file.txt")
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_read_directory(self, file_tool, temp_dir):
        """Test that reading a directory fails."""
        result = await file_tool.read_file(str(temp_dir))
        
        assert result["success"] is False
        assert "not a file" in result["error"]
    
    @pytest.mark.asyncio
    async def test_write_text_file(self, file_tool, temp_dir):
        """Test writing a text file."""
        test_file = temp_dir / "output.txt"
        test_content = "Test content"
        
        result = await file_tool.write_file(
            str(test_file),
            test_content
        )
        
        assert result["success"] is True
        assert test_file.exists()
        assert test_file.read_text() == test_content
    
    @pytest.mark.asyncio
    async def test_write_with_directory_creation(self, file_tool, temp_dir):
        """Test writing a file with automatic directory creation."""
        test_file = temp_dir / "subdir" / "output.txt"
        test_content = "Test content"
        
        result = await file_tool.write_file(
            str(test_file),
            test_content,
            create_dirs=True
        )
        
        assert result["success"] is True
        assert test_file.exists()
        assert test_file.read_text() == test_content
    
    @pytest.mark.asyncio
    async def test_write_without_directory_creation(self, file_tool, temp_dir):
        """Test that writing fails when directory doesn't exist."""
        test_file = temp_dir / "nonexistent" / "output.txt"
        
        result = await file_tool.write_file(
            str(test_file),
            "content",
            create_dirs=False
        )
        
        assert result["success"] is False
        assert "does not exist" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_directory(self, file_tool, temp_dir):
        """Test listing directory contents."""
        # Create test files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        (temp_dir / "subdir").mkdir()
        
        result = await file_tool.list_directory(str(temp_dir))
        
        assert result["success"] is True
        assert result["count"] == 3
        
        # Check that files are listed
        file_names = [f["name"] for f in result["files"]]
        assert "file1.txt" in file_names
        assert "file2.txt" in file_names
        assert "subdir" in file_names
    
    @pytest.mark.asyncio
    async def test_list_directory_with_pattern(self, file_tool, temp_dir):
        """Test listing directory with pattern filter."""
        # Create test files
        (temp_dir / "test1.txt").write_text("content")
        (temp_dir / "test2.txt").write_text("content")
        (temp_dir / "other.log").write_text("content")
        
        result = await file_tool.list_directory(
            str(temp_dir),
            pattern="*.txt"
        )
        
        assert result["success"] is True
        assert result["count"] == 2
        
        file_names = [f["name"] for f in result["files"]]
        assert "test1.txt" in file_names
        assert "test2.txt" in file_names
        assert "other.log" not in file_names
    
    @pytest.mark.asyncio
    async def test_list_directory_recursive(self, file_tool, temp_dir):
        """Test recursive directory listing."""
        # Create nested structure
        (temp_dir / "file1.txt").write_text("content")
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("content")
        
        result = await file_tool.list_directory(
            str(temp_dir),
            recursive=True
        )
        
        assert result["success"] is True
        assert result["count"] >= 3  # At least 2 files and 1 directory
    
    @pytest.mark.asyncio
    async def test_file_extension_validation(self, file_tool, temp_dir):
        """Test that file extension validation works."""
        # Try to read a file with disallowed extension
        test_file = temp_dir / "test.exe"
        test_file.write_text("content")
        
        result = await file_tool.read_file(str(test_file))
        
        assert result["success"] is False
        assert "not allowed" in result["error"]
        assert result["allowed_extensions"] == [".txt", ".json", ".yaml", ".yml"]