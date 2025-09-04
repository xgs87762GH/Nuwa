import json
from dataclasses import dataclass
from typing import List


@dataclass
class PluginSelectionMata:
    """插件选择元数据"""
    plugin_name: str
    plugin_id: str
    reason: str
    confidence: float


@dataclass
class PluginsSelection:
    analysis: str = ""
    selected_plugins: List[PluginSelectionMata] = None
    overall_confidence: float = 0.0

    @classmethod
    def from_content(cls, content: str) -> "PluginsSelection":
        """Create PluginSelection from AI response content"""
        try:
            data = json.loads(content)
            # Validate required fields
            required_fields = ["analysis", "selected_plugins", "overall_confidence"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")

            # Create plugin metadata list
            plugin_metas = []
            for plugin_data in data["selected_plugins"]:
                plugin_meta = PluginSelectionMata(
                    plugin_name=plugin_data["plugin_name"],
                    plugin_id=plugin_data["plugin_id"],
                    reason=plugin_data["reason"],
                    confidence=float(plugin_data["confidence"])
                )
                plugin_metas.append(plugin_meta)

            return cls(
                analysis=data["analysis"],
                selected_plugins=plugin_metas,
                overall_confidence=float(data["overall_confidence"])
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid data format: {str(e)}")
