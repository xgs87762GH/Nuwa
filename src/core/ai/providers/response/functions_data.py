import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FunctionSelection:
    """选中的函数信息"""
    plugin_name: str
    plugin_id: str
    function_name: str
    full_method_name: str
    description: str
    reason: str
    confidence: float
    required_params: List[str] = field(default_factory=list)
    suggested_params: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FunctionSelection':
        """从字典创建实例"""
        return cls(
            plugin_name=data["plugin_name"],
            plugin_id=data["plugin_id"],
            function_name=data["function_name"],
            full_method_name=data["full_method_name"],
            description=data["description"],
            reason=data["reason"],
            confidence=float(data["confidence"]),
            required_params=data.get("required_params", []),
            suggested_params=data.get("suggested_params", {})
        )


@dataclass
class ExecutionPlan:
    """执行计划"""
    analysis: str = ""
    selected_functions: List[FunctionSelection] = field(default_factory=list)
    execution_order: List[int] = field(default_factory=list)
    overall_confidence: float = 0.0

    @classmethod
    def from_content(cls, content: str) -> "ExecutionPlan":
        """从AI响应内容创建执行计划"""
        try:
            data = json.loads(content)

            # 验证必需字段
            required_fields = ["analysis", "selected_functions", "execution_order", "overall_confidence"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")

            # 创建函数列表
            functions = []
            for func_data in data["selected_functions"]:
                function = FunctionSelection.from_dict(func_data)
                functions.append(function)

            return cls(
                analysis=data["analysis"],
                selected_functions=functions,
                execution_order=data["execution_order"],
                overall_confidence=float(data["overall_confidence"])
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid data format: {str(e)}")

    def get_ordered_functions(self) -> List[FunctionSelection]:
        """按执行顺序获取函数列表"""
        ordered_functions = []
        for order in self.execution_order:
            if 1 <= order <= len(self.selected_functions):
                ordered_functions.append(self.selected_functions[order - 1])
        return ordered_functions
