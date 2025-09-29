import os

from services import CameraService


class CameraPlugin:

    @classmethod
    def PLUGIN_CONFIG(cls):
        return {
            "output": {
                "type": ["string"],
                "default": "output",
                "description": "Output directory for camera files",
                "required": False
            }
        }
    @classmethod
    def FUNCTIONS(cls):
        json_path = os.path.join(os.path.dirname(__file__), "tools/function_schema.json")
        with open(json_path, 'r', encoding="utf-8") as f:
            import json
            return json.load(f)

    @classmethod
    def GET_PLUGIN(cls):
        return {
            "plugin_id": "camera_plugin",
            "instance": CameraService
        }


__all__ = ["CameraPlugin"]


if __name__ == '__main__':
    print(CameraPlugin.GET_PLUGIN())