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

    # @classmethod
    # def METADATA(self):
    #     return {
    #         "name": "Camera Plugin",
    #         "description": "Plugin for camera operations and configurations",
    #         "version": "1.0.0",
    #         "author": "Gordon",
    #         "email": "Gordon@gmail.com",
    #         "license": "MIT",
    #         "link": [{
    #             "name": "GitHub",
    #             "url": ""
    #         }],
    #         "tags": ["camera", "recording", "photo", "video"],
    #         "created_at": "2025-08-22 00:00:00",
    #         "updated_at": "2025-08-22 00:00:00",
    #         "category": "camera"
    #     }

    @classmethod
    def FUNCTIONS(cls):
        print(os.path.join(os.path.dirname(__file__), "function_schema.json"))
        with open(os.path.join(os.path.dirname(__file__), "tools/function_schema.json"), 'r', encoding="utf-8") as f:
            return f.read()

    @classmethod
    def GET_PLUGIN(cls):
        return {
            "plugin_id": "camera_plugin",
            "instance": CameraService
        }


__all__ = ["CameraPlugin"]


if __name__ == '__main__':
    print(CameraPlugin.GET_PLUGIN())