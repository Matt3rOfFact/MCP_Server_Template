"""Tools module for MCP Server."""

from .calculator import CalculatorTool
from .file_operations import FileOperationsTool
from .web_scraper import WebScraperTool
from .data_processor import DataProcessorTool

# Initialize tool instances
calculator_tool = CalculatorTool()
file_operations_tool = FileOperationsTool()
web_scraper_tool = WebScraperTool()
data_processor_tool = DataProcessorTool()

__all__ = [
    "calculator_tool",
    "file_operations_tool",
    "web_scraper_tool",
    "data_processor_tool",
    "CalculatorTool",
    "FileOperationsTool",
    "WebScraperTool",
    "DataProcessorTool",
]