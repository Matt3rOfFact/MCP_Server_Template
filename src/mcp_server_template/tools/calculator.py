"""Calculator tool for mathematical operations."""

from typing import Any, Dict
import math


class CalculatorTool:
    """Tool for performing mathematical calculations."""
    
    async def calculate(self, operation: str, a: float, b: float) -> Dict[str, Any]:
        """
        Perform a mathematical calculation.
        
        Args:
            operation: The operation to perform
            a: First number
            b: Second number
            
        Returns:
            Dictionary containing the result or error
        """
        try:
            operations = {
                "add": lambda x, y: x + y,
                "subtract": lambda x, y: x - y,
                "multiply": lambda x, y: x * y,
                "divide": lambda x, y: x / y if y != 0 else None,
                "power": lambda x, y: x ** y,
                "modulo": lambda x, y: x % y if y != 0 else None,
            }
            
            if operation not in operations:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": list(operations.keys())
                }
            
            result = operations[operation](a, b)
            
            if result is None:
                return {
                    "success": False,
                    "error": "Division by zero"
                }
            
            return {
                "success": True,
                "operation": operation,
                "a": a,
                "b": b,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def advanced_calculate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Dictionary containing the result or error
        """
        try:
            # Define safe functions that can be used in expressions
            safe_dict = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e,
            }
            
            # Evaluate the expression in a restricted environment
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            return {
                "success": True,
                "expression": expression,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "hint": "Ensure your expression uses only allowed functions and operators"
            }