"""Unit tests for calculator tool."""

import pytest
from mcp_server_template.tools.calculator import CalculatorTool


@pytest.fixture
def calculator():
    """Create a calculator tool instance."""
    return CalculatorTool()


class TestCalculatorTool:
    """Test suite for CalculatorTool."""
    
    @pytest.mark.asyncio
    async def test_addition(self, calculator):
        """Test addition operation."""
        result = await calculator.calculate("add", 5, 3)
        assert result["success"] is True
        assert result["result"] == 8
        assert result["operation"] == "add"
    
    @pytest.mark.asyncio
    async def test_subtraction(self, calculator):
        """Test subtraction operation."""
        result = await calculator.calculate("subtract", 10, 4)
        assert result["success"] is True
        assert result["result"] == 6
        assert result["operation"] == "subtract"
    
    @pytest.mark.asyncio
    async def test_multiplication(self, calculator):
        """Test multiplication operation."""
        result = await calculator.calculate("multiply", 6, 7)
        assert result["success"] is True
        assert result["result"] == 42
        assert result["operation"] == "multiply"
    
    @pytest.mark.asyncio
    async def test_division(self, calculator):
        """Test division operation."""
        result = await calculator.calculate("divide", 15, 3)
        assert result["success"] is True
        assert result["result"] == 5
        assert result["operation"] == "divide"
    
    @pytest.mark.asyncio
    async def test_division_by_zero(self, calculator):
        """Test division by zero handling."""
        result = await calculator.calculate("divide", 10, 0)
        assert result["success"] is False
        assert "Division by zero" in result["error"]
    
    @pytest.mark.asyncio
    async def test_power(self, calculator):
        """Test power operation."""
        result = await calculator.calculate("power", 2, 3)
        assert result["success"] is True
        assert result["result"] == 8
        assert result["operation"] == "power"
    
    @pytest.mark.asyncio
    async def test_modulo(self, calculator):
        """Test modulo operation."""
        result = await calculator.calculate("modulo", 10, 3)
        assert result["success"] is True
        assert result["result"] == 1
        assert result["operation"] == "modulo"
    
    @pytest.mark.asyncio
    async def test_unknown_operation(self, calculator):
        """Test handling of unknown operation."""
        result = await calculator.calculate("unknown", 5, 3)
        assert result["success"] is False
        assert "Unknown operation" in result["error"]
        assert "available_operations" in result
    
    @pytest.mark.asyncio
    async def test_advanced_calculate_simple(self, calculator):
        """Test advanced calculate with simple expression."""
        result = await calculator.advanced_calculate("2 + 3 * 4")
        assert result["success"] is True
        assert result["result"] == 14
    
    @pytest.mark.asyncio
    async def test_advanced_calculate_with_functions(self, calculator):
        """Test advanced calculate with math functions."""
        result = await calculator.advanced_calculate("sqrt(16) + abs(-5)")
        assert result["success"] is True
        assert result["result"] == 9
    
    @pytest.mark.asyncio
    async def test_advanced_calculate_with_constants(self, calculator):
        """Test advanced calculate with math constants."""
        result = await calculator.advanced_calculate("pi * 2")
        assert result["success"] is True
        assert abs(result["result"] - 6.283185307179586) < 0.0001
    
    @pytest.mark.asyncio
    async def test_advanced_calculate_invalid(self, calculator):
        """Test advanced calculate with invalid expression."""
        result = await calculator.advanced_calculate("2 + invalid")
        assert result["success"] is False
        assert "error" in result
        assert "hint" in result
    
    @pytest.mark.asyncio
    async def test_advanced_calculate_dangerous(self, calculator):
        """Test that dangerous operations are blocked."""
        result = await calculator.advanced_calculate("__import__('os').system('ls')")
        assert result["success"] is False
        # Should fail because __import__ is not in safe_dict