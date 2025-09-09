from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict

from src.core.ai.providers.response import FunctionSelection, ExecutionPlan, PluginSelectionMata

"""
Plan Models
Contains models related to the plan service
"""


@dataclass
class PlanResult:
    success: bool = False
    user_input: Optional[str] = None
    selected_plugins: Optional[List[PluginSelectionMata]] = field(default_factory=list)
    plugin_functions: Optional[List[FunctionSelection]] = field(default_factory=list)
    execution_plan: Optional[ExecutionPlan] = None
    error: Optional[str] = None
    suggestion: Optional[str] = None

    @staticmethod
    def error_result(error: str, user_input: Optional[str] = None,
                     selected_plugins: Optional[List[PluginSelectionMata]] = None,
                     suggestion: Optional[str] = None) -> "PlanResult":
        return PlanResult(
            success=False,
            error=error,
            user_input=user_input,
            selected_plugins=selected_plugins if selected_plugins is not None else [],
            suggestion=suggestion
        )
    @staticmethod
    def success_result(user_input: str, selected_plugins: List[PluginSelectionMata], plugin_functions: List[Any],
                       execution_plan: Any) -> "PlanResult":
        return PlanResult(
            success=True,
            user_input=user_input,
            selected_plugins=selected_plugins,
            plugin_functions=plugin_functions,
            execution_plan=execution_plan
        )
    def selected_plugins_to_dict(self) -> List[Dict[str, Any]]:
        return [plugin.to_dict() for plugin in self.selected_plugins]

    def plugin_functions_to_dict(self) -> List[Dict[str, Any]]:
        print(f"plugin_functions type: {type(self.plugin_functions)}")
        if self.plugin_functions:
            print(f"First item type: {type(self.plugin_functions[0])}")
            print(f"First item content: {self.plugin_functions[0]}")

        return [
            plugin.to_dict() if hasattr(plugin, 'to_dict') else plugin
            for plugin in self.plugin_functions or []
        ]


@dataclass
class AIStatusResult:
    available_providers: List[str] = field(default_factory=list)
    provider_types: List[str] = field(default_factory=list)
    health_status: Optional[str] = None
    preferred_provider: Optional[str] = None
    fallback_providers: Optional[List[str]] = None
    error: Optional[str] = None

    @staticmethod
    def error_result(error: str) -> "AIStatusResult":
        return AIStatusResult(error=error)


from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PluginStatusResult:
    total_plugins: int
    available_plugins: int
    plugin_names: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @staticmethod
    def error_result(error: str) -> "PluginStatusResult":
        return PluginStatusResult(total_plugins=0, available_plugins=0, plugin_names=[], error=error)


__all__ = [
    "PlanResult",
    "AIStatusResult",
    "PluginStatusResult"
]
