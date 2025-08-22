"""Data processor tool for data transformation and analysis."""

from typing import Any, Dict, List, Optional, Union
import statistics
import json
from collections import Counter
from datetime import datetime


class DataProcessorTool:
    """Tool for data processing operations."""
    
    async def process(
        self,
        data: List[Any],
        operation: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process data with various operations.
        
        Args:
            data: Input data list
            operation: Operation to perform
            options: Additional options for the operation
            
        Returns:
            Dictionary containing processed data or error
        """
        try:
            options = options or {}
            
            operations = {
                "filter": self._filter_data,
                "map": self._map_data,
                "reduce": self._reduce_data,
                "sort": self._sort_data,
                "group": self._group_data,
                "aggregate": self._aggregate_data,
                "unique": self._unique_data,
                "sample": self._sample_data,
                "statistics": self._calculate_statistics,
            }
            
            if operation not in operations:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": list(operations.keys())
                }
            
            result = await operations[operation](data, options)
            
            return {
                "success": True,
                "operation": operation,
                "input_count": len(data),
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _filter_data(self, data: List[Any], options: Dict[str, Any]) -> List[Any]:
        """Filter data based on conditions."""
        condition = options.get("condition", "")
        field = options.get("field")
        value = options.get("value")
        operator = options.get("operator", "==")
        
        if not condition and not field:
            return data
        
        filtered = []
        for item in data:
            if condition:
                # Use simple eval for basic conditions (be careful in production)
                try:
                    if eval(condition, {"item": item}):
                        filtered.append(item)
                except:
                    pass
            elif field and isinstance(item, dict):
                item_value = item.get(field)
                if self._compare_values(item_value, value, operator):
                    filtered.append(item)
        
        return filtered
    
    async def _map_data(self, data: List[Any], options: Dict[str, Any]) -> List[Any]:
        """Transform each element in the data."""
        transform = options.get("transform", "")
        field = options.get("field")
        
        if not transform and not field:
            return data
        
        mapped = []
        for item in data:
            if transform:
                try:
                    # Simple transformation (be careful in production)
                    result = eval(transform, {"item": item})
                    mapped.append(result)
                except:
                    mapped.append(item)
            elif field and isinstance(item, dict):
                mapped.append(item.get(field))
            else:
                mapped.append(item)
        
        return mapped
    
    async def _reduce_data(self, data: List[Any], options: Dict[str, Any]) -> Any:
        """Reduce data to a single value."""
        operation = options.get("reduce_operation", "sum")
        initial = options.get("initial", 0)
        
        if operation == "sum":
            return sum(data, initial)
        elif operation == "product":
            result = initial if initial != 0 else 1
            for item in data:
                result *= item
            return result
        elif operation == "concat":
            return "".join(str(item) for item in data)
        elif operation == "count":
            return len(data)
        else:
            return data
    
    async def _sort_data(self, data: List[Any], options: Dict[str, Any]) -> List[Any]:
        """Sort data."""
        reverse = options.get("reverse", False)
        key = options.get("key")
        
        if key and all(isinstance(item, dict) for item in data):
            return sorted(data, key=lambda x: x.get(key, ""), reverse=reverse)
        else:
            return sorted(data, reverse=reverse)
    
    async def _group_data(self, data: List[Any], options: Dict[str, Any]) -> Dict[str, List[Any]]:
        """Group data by a field."""
        field = options.get("field", "")
        
        if not field:
            return {"all": data}
        
        groups = {}
        for item in data:
            if isinstance(item, dict):
                key = str(item.get(field, "unknown"))
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)
        
        return groups
    
    async def _aggregate_data(self, data: List[Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data with multiple operations."""
        aggregations = options.get("aggregations", ["count"])
        field = options.get("field")
        
        results = {}
        
        # Extract numeric values if field is specified
        if field and all(isinstance(item, dict) for item in data):
            values = [item.get(field) for item in data if isinstance(item.get(field), (int, float))]
        else:
            values = [item for item in data if isinstance(item, (int, float))]
        
        for agg in aggregations:
            if agg == "count":
                results["count"] = len(data)
            elif agg == "sum" and values:
                results["sum"] = sum(values)
            elif agg == "avg" and values:
                results["avg"] = statistics.mean(values)
            elif agg == "min" and values:
                results["min"] = min(values)
            elif agg == "max" and values:
                results["max"] = max(values)
            elif agg == "median" and values:
                results["median"] = statistics.median(values)
            elif agg == "mode" and values:
                try:
                    results["mode"] = statistics.mode(values)
                except statistics.StatisticsError:
                    results["mode"] = None
        
        return results
    
    async def _unique_data(self, data: List[Any], options: Dict[str, Any]) -> List[Any]:
        """Get unique values from data."""
        field = options.get("field")
        
        if field and all(isinstance(item, dict) for item in data):
            seen = set()
            unique = []
            for item in data:
                value = item.get(field)
                if value not in seen:
                    seen.add(value)
                    unique.append(item)
            return unique
        else:
            # For non-dict items, convert to string for uniqueness
            seen = set()
            unique = []
            for item in data:
                key = str(item)
                if key not in seen:
                    seen.add(key)
                    unique.append(item)
            return unique
    
    async def _sample_data(self, data: List[Any], options: Dict[str, Any]) -> List[Any]:
        """Sample random elements from data."""
        import random
        
        size = options.get("size", 10)
        seed = options.get("seed")
        
        if seed:
            random.seed(seed)
        
        size = min(size, len(data))
        return random.sample(data, size)
    
    async def _calculate_statistics(self, data: List[Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive statistics for numeric data."""
        field = options.get("field")
        
        # Extract numeric values
        if field and all(isinstance(item, dict) for item in data):
            values = [item.get(field) for item in data if isinstance(item.get(field), (int, float))]
        else:
            values = [item for item in data if isinstance(item, (int, float))]
        
        if not values:
            return {"error": "No numeric values found"}
        
        stats = {
            "count": len(values),
            "sum": sum(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "range": max(values) - min(values),
        }
        
        if len(values) > 1:
            stats["stdev"] = statistics.stdev(values)
            stats["variance"] = statistics.variance(values)
        
        # Calculate quartiles
        if len(values) >= 4:
            sorted_values = sorted(values)
            n = len(sorted_values)
            stats["q1"] = sorted_values[n // 4]
            stats["q3"] = sorted_values[3 * n // 4]
            stats["iqr"] = stats["q3"] - stats["q1"]
        
        # Frequency distribution
        counter = Counter(values)
        stats["frequency"] = dict(counter.most_common(10))
        
        return stats
    
    def _compare_values(self, value1: Any, value2: Any, operator: str) -> bool:
        """Compare two values with the given operator."""
        try:
            if operator == "==":
                return value1 == value2
            elif operator == "!=":
                return value1 != value2
            elif operator == ">":
                return value1 > value2
            elif operator == ">=":
                return value1 >= value2
            elif operator == "<":
                return value1 < value2
            elif operator == "<=":
                return value1 <= value2
            elif operator == "in":
                return value1 in value2
            elif operator == "not_in":
                return value1 not in value2
            elif operator == "contains":
                return value2 in value1
            else:
                return False
        except:
            return False