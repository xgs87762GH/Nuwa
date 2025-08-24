import logging
from typing import Dict, Optional

import cv2


logger = logging.getLogger(__name__)

class OpenCVPropertyMapper:
    """Unified OpenCV property mapping manager"""

    # Property mapping table
    PROPERTY_MAPPING = {
        'width': cv2.CAP_PROP_FRAME_WIDTH,
        'height': cv2.CAP_PROP_FRAME_HEIGHT,
        'brightness': cv2.CAP_PROP_BRIGHTNESS,
        'contrast': cv2.CAP_PROP_CONTRAST,
        'saturation': cv2.CAP_PROP_SATURATION,
        'hue': cv2.CAP_PROP_HUE,
        'gain': cv2.CAP_PROP_GAIN,
        'exposure': cv2.CAP_PROP_EXPOSURE,
        'auto_focus': cv2.CAP_PROP_AUTOFOCUS,
        'focus': cv2.CAP_PROP_FOCUS,
        'fps': cv2.CAP_PROP_FPS,
    }

    # Reverse mapping
    REVERSE_MAPPING = {v: k for k, v in PROPERTY_MAPPING.items()}

    # Properties needing 0-1 normalization
    NORMALIZED_PROPERTIES = {
        'brightness', 'contrast', 'saturation', 'hue',
        'gain', 'exposure', 'focus'
    }

    @classmethod
    def get_cv2_property(cls, param_name: str) -> Optional[int]:
        """Get OpenCV property constant for parameter"""
        return cls.PROPERTY_MAPPING.get(param_name)

    @classmethod
    def get_param_name(cls, cv2_prop: int) -> str:
        """Get parameter name from OpenCV property constant"""
        return cls.REVERSE_MAPPING.get(cv2_prop, f'property_{cv2_prop}')

    @classmethod
    def needs_normalization(cls, param_name: str) -> bool:
        """Check if parameter needs normalization mapping"""
        return param_name in cls.NORMALIZED_PROPERTIES

    @classmethod
    def get_all_mappable_params(cls) -> Dict[str, int]:
        """Get all mappable parameters"""
        return cls.PROPERTY_MAPPING.copy()


class ParameterMapper:
    """Maps 0-1 normalized values to camera's actual ranges"""

    def __init__(self):
        self.ranges = {}

    def detect_range(self, camera, param_name, cv2_prop):
        """Detect actual range for single parameter"""
        current = camera.get(cv2_prop)

        camera.set(cv2_prop, -1000)
        min_val = camera.get(cv2_prop)

        camera.set(cv2_prop, 1000)
        max_val = camera.get(cv2_prop)

        camera.set(cv2_prop, current)

        self.ranges[param_name] = {
            'min': min_val,
            'max': max_val,
            'current': current
        }

        return self.ranges[param_name]

    def detect_all_ranges(self, camera):
        """Detect ranges for all normalized parameters"""
        for param_name in OpenCVPropertyMapper.NORMALIZED_PROPERTIES:
            cv2_prop = OpenCVPropertyMapper.get_cv2_property(param_name)
            if cv2_prop is not None:
                try:
                    self.detect_range(camera, param_name, cv2_prop)
                    logger.debug(f"Detected {param_name} range: {self.ranges[param_name]}")
                except Exception as e:
                    logger.warning(f"Cannot detect {param_name} range: {e}")

    def normalize_to_camera(self, param_name, normalized_value):
        """Convert 0-1 value to camera's actual value"""
        if param_name not in self.ranges:
            return normalized_value

        range_info = self.ranges[param_name]
        min_val = range_info['min']
        max_val = range_info['max']

        return min_val + (max_val - min_val) * normalized_value

