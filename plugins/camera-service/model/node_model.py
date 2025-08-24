"""
MCP 节点基础定义框架
"""

from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class MCPParameter:
    """MCP 参数定义"""
    name: str
    type: str  # "string", "int", "float", "bool", "array", "object"
    description: str = ""
    required: bool = True
    default: Any = None
    constraints: Optional[Dict[str, Any]] = None  # {"min": 0, "max": 100, "enum": ["a", "b"]}

    def to_schema(self) -> Dict[str, Any]:
        """转换为参数 schema"""
        schema = {
            "type": self.type,
            "description": self.description
        }

        if self.default is not None:
            schema["default"] = self.default

        if self.constraints:
            schema.update(self.constraints)

        return schema


@dataclass
class MCPFunction:
    """MCP 函数定义"""
    name: str
    description: str
    parameters: List[MCPParameter] = field(default_factory=list)
    return_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)

    def to_schema(self) -> Dict[str, Any]:
        """转换为函数 schema"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    param.name: param.to_schema()
                    for param in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required]
            },
            "returns": self.return_schema,
            "examples": self.examples
        }


@dataclass
class MCPService:
    """MCP 服务定义"""
    name: str
    version: str
    description: str
    global_parameters: List[MCPParameter] = field(default_factory=list)
    functions: List[MCPFunction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_schema(self) -> Dict[str, Any]:
        """转换为完整服务 schema"""
        return {
            "service": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "metadata": self.metadata
            },
            "global_parameters": {
                param.name: param.to_schema()
                for param in self.global_parameters
            },
            "functions": {
                func.name: func.to_schema()
                for func in self.functions
            }
        }


class MCPNode(ABC):
    """MCP 节点基类"""

    @classmethod
    @abstractmethod
    def get_service_definition(cls) -> MCPService:
        """获取服务定义"""
        pass

    def __init__(self, **global_params):
        """初始化节点，传入全局参数"""
        self.global_params = global_params
        self._validate_global_params()

    def _validate_global_params(self):
        """验证全局参数"""
        service_def = self.get_service_definition()
        for param in service_def.global_parameters:
            if param.required and param.name not in self.global_params:
                # 如果有默认值，使用默认值
                if param.default is not None:
                    self.global_params[param.name] = param.default
                else:
                    raise ValueError(f"缺少必需的全局参数: {param.name}")

    @abstractmethod
    def execute_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """执行指定函数"""
        pass

    def get_service_schema(self) -> Dict[str, Any]:
        """获取服务完整 schema"""
        return self.get_service_definition().to_schema()

    def list_functions(self) -> List[str]:
        """列出所有可用函数"""
        return [func.name for func in self.get_service_definition().functions]

    def get_function_schema(self, function_name: str) -> Optional[Dict[str, Any]]:
        """获取指定函数的 schema"""
        service_def = self.get_service_definition()
        for func in service_def.functions:
            if func.name == function_name:
                return func.to_schema()
        return None

    def validate_function_params(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """验证函数参数"""
        func_schema = self.get_function_schema(function_name)
        if not func_schema:
            return {"valid": False, "error": f"Unknown function: {function_name}"}

        required_params = func_schema["parameters"].get("required", [])
        properties = func_schema["parameters"].get("properties", {})

        errors = []

        # 检查必需参数
        for param in required_params:
            if param not in kwargs:
                errors.append(f"Missing required parameter: {param}")

        # 检查参数类型和约束（简化版）
        for param_name, param_value in kwargs.items():
            if param_name in properties:
                param_schema = properties[param_name]
                # 这里可以添加更详细的类型验证
                # 暂时只做基本检查
                continue

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }