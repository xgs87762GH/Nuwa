"""Camera model with simplified validation - auto-detection provides defaults."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
import cv2

from core.exceptions import ValidationError
from utils.camera_param_mapper import ParameterMapper, OpenCVPropertyMapper

logger = logging.getLogger(__name__)


class CameraDefaultDetector:
    """Detects and manages camera default values"""

    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self._detected_defaults = None

    def detect_camera_defaults(self) -> Dict[str, Any]:
        """Detect actual camera default values"""
        if self._detected_defaults is not None:
            return self._detected_defaults

        try:
            camera = cv2.VideoCapture(self.camera_id)
            if not camera.isOpened():
                logger.warning(f"Cannot open camera {self.camera_id} for default detection")
                return self._get_fallback_defaults()

            defaults = {}

            # Detect basic properties
            defaults['width'] = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            defaults['height'] = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            defaults['fps'] = camera.get(cv2.CAP_PROP_FPS)

            # Detect adjustable parameters
            for param_name, cv2_prop in OpenCVPropertyMapper.PROPERTY_MAPPING.items():
                if param_name in ['width', 'height', 'fps']:
                    continue  # Already handled above

                try:
                    value = camera.get(cv2_prop)

                    # Special handling for boolean parameters
                    if param_name == 'auto_focus':
                        defaults[param_name] = bool(value) if value >= 0 else True  # Default to True
                    elif OpenCVPropertyMapper.needs_normalization(param_name):
                        # For normalized parameters, convert to standard range
                        defaults[param_name] = self._normalize_camera_value(param_name, value)
                    else:
                        defaults[param_name] = value

                except Exception as e:
                    logger.debug(f"Cannot detect default for {param_name}: {e}")
                    defaults[param_name] = self._get_safe_default(param_name)

            camera.release()
            self._detected_defaults = defaults

            logger.info(f"Detected camera defaults for camera {self.camera_id}")
            return defaults

        except Exception as e:
            logger.error(f"Failed to detect camera defaults: {e}")
            return self._get_fallback_defaults()

    def _normalize_camera_value(self, param_name: str, camera_value: Any) -> float:
        """Normalize camera value to standard range"""
        if camera_value is None:
            return self._get_safe_default(param_name)

        if param_name == 'hue':
            # Normalize to -180 to 180 range, then to -1 to 1
            if abs(camera_value) <= 180:
                return camera_value / 180.0
            return 0.0

        elif param_name in ['brightness', 'contrast', 'saturation']:
            # Often 0-100 in cameras, normalize to -1 to 1 (0 = neutral)
            if 0 <= camera_value <= 100:
                return (camera_value - 50) / 50.0
            elif -1 <= camera_value <= 1:
                return camera_value
            return 0.0  # Neutral

        elif param_name in ['gain', 'exposure', 'focus']:
            # Often 0-100 in cameras, normalize to 0-1
            if 0 <= camera_value <= 100:
                return camera_value / 100.0
            elif 0 <= camera_value <= 1:
                return camera_value
            return 0.0

        return 0.0  # Safe default

    def _get_safe_default(self, param_name: str) -> Any:
        """Get safe default value for parameter"""
        safe_defaults = {
            'brightness': 0.0,      # Neutral
            'contrast': 0.0,        # Neutral
            'saturation': 0.0,      # Neutral
            'hue': 0.0,            # No shift
            'gain': 0.0,           # Low gain
            'exposure': -1.0,       # Auto exposure
            'auto_focus': True,     # Enable autofocus
            'focus': 0.5,          # Mid-range focus
        }
        return safe_defaults.get(param_name, 0.0)

    def _get_fallback_defaults(self) -> Dict[str, Any]:
        """Fallback defaults when detection fails"""
        return {
            'width': 640,
            'height': 480,
            'fps': 30.0,
            'brightness': 0.0,
            'contrast': 0.0,
            'saturation': 0.0,
            'hue': 0.0,
            'gain': 0.0,
            'exposure': -1.0,
            'auto_focus': True,
            'focus': 0.5
        }


@dataclass
class CameraParameterBase:
    """
    Camera configuration model with intelligent defaults and minimal validation.

    All parameters except output_dir have automatic defaults from camera detection.
    Validation is simplified since all values are guaranteed to be reasonable.
    """

    # Basic configuration - only camera_id and output_dir need explicit validation
    camera_id: int = field(
        default=0,
        metadata={"description": "Camera device ID (0 for default camera)"}
    )

    output_dir: Union[str, Path] = field(
        default="output",
        metadata={"description": "Output directory for captured media"}
    )

    # All other parameters get intelligent defaults - minimal metadata needed
    width: Optional[int] = field(
        default=None,
        metadata={"description": "Frame width in pixels (None = auto-detect)"}
    )

    height: Optional[int] = field(
        default=None,
        metadata={"description": "Frame height in pixels (None = auto-detect)"}
    )

    brightness: Optional[float] = field(
        default=None,
        metadata={"description": "Brightness adjustment (None = auto-detect)"}
    )

    contrast: Optional[float] = field(
        default=None,
        metadata={"description": "Contrast adjustment (None = auto-detect)"}
    )

    saturation: Optional[float] = field(
        default=None,
        metadata={"description": "Color saturation (None = auto-detect)"}
    )

    hue: Optional[float] = field(
        default=None,
        metadata={"description": "Hue adjustment (None = auto-detect)"}
    )

    gain: Optional[float] = field(
        default=None,
        metadata={"description": "Camera gain/ISO sensitivity (None = auto-detect)"}
    )

    exposure: Optional[float] = field(
        default=None,
        metadata={"description": "Exposure value (None = auto-detect)"}
    )

    auto_focus: Optional[bool] = field(
        default=None,
        metadata={"description": "Enable automatic focus (None = auto-detect)"}
    )

    focus: Optional[float] = field(
        default=None,
        metadata={"description": "Manual focus value (None = auto-detect)"}
    )

    def __post_init__(self):
        """Initialize with intelligent defaults and minimal validation"""
        # Basic validation for required fields
        self._validate_basic_requirements()

        # Convert string path to Path object
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)

        # Auto-detect and apply defaults for None values
        self._apply_intelligent_defaults()

        # Initialize parameter mapper
        self.mapper = ParameterMapper()
        self._initialized = False
        self._detector = CameraDefaultDetector(self.camera_id)

        logger.info(f"Camera model initialized with auto-detected defaults - User: Gordon, Time: 2025-08-21 06:27:56")

    def _validate_basic_requirements(self) -> None:
        """Validate only essential requirements"""
        # Validate camera_id
        if not isinstance(self.camera_id, int) or self.camera_id < 0:
            raise ValidationError("Camera ID must be a non-negative integer")

        # Validate output_dir
        if not isinstance(self.output_dir, (str, Path)):
            raise ValidationError("Output directory must be a string or Path object")

    def _apply_intelligent_defaults(self) -> None:
        """Apply intelligent defaults for parameters that are None"""
        detector = CameraDefaultDetector(self.camera_id)
        detected_defaults = detector.detect_camera_defaults()

        applied_defaults = {}

        for field_name in self.__dataclass_fields__:
            # Skip basic config fields
            if field_name in ['camera_id', 'output_dir']:
                continue

            current_value = getattr(self, field_name)

            # Apply default if current value is None
            if current_value is None:
                default_value = detected_defaults.get(field_name)
                if default_value is not None:
                    setattr(self, field_name, default_value)
                    applied_defaults[field_name] = default_value

        if applied_defaults:
            logger.debug(f"Applied auto-detected defaults: {list(applied_defaults.keys())}")

    def update_parameters(self, **kwargs) -> Dict[str, Any]:
        """Update camera parameters with automatic validation"""
        changes = {}
        errors = {}

        for param_name, new_value in kwargs.items():
            if not hasattr(self, param_name):
                errors[param_name] = f"Unknown parameter: {param_name}"
                continue

            old_value = getattr(self, param_name)

            try:
                # Only validate basic constraints for critical parameters
                if param_name == 'camera_id':
                    if not isinstance(new_value, int) or new_value < 0:
                        raise ValidationError("Camera ID must be a non-negative integer")
                elif param_name == 'output_dir':
                    if not isinstance(new_value, (str, Path)):
                        raise ValidationError("Output directory must be a string or Path object")

                # For other parameters, trust that auto-detection provides reasonable ranges
                # Users can set any reasonable value
                setattr(self, param_name, new_value)

                # Track successful change
                if old_value != new_value:
                    changes[param_name] = {'old': old_value, 'new': new_value}
                    logger.debug(f"Updated {param_name}: {old_value} -> {new_value}")

            except ValidationError as e:
                # Revert on validation error
                setattr(self, param_name, old_value)
                errors[param_name] = str(e)
                logger.warning(f"Failed to update {param_name}: {e}")

        result = {'changes': changes}
        if errors:
            result['errors'] = errors

        return result

    def get_opencv_properties(self) -> Dict[int, float]:
        """Convert camera parameters to OpenCV property constants"""
        props = {}

        # All parameters should have values now (either user-set or auto-detected)
        for param_name in OpenCVPropertyMapper.get_all_mappable_params():
            value = getattr(self, param_name, None)
            if value is None:
                continue

            cv2_prop = OpenCVPropertyMapper.get_cv2_property(param_name)
            if cv2_prop is None:
                continue

            # Special handling for auto_focus
            if param_name == 'auto_focus':
                props[cv2_prop] = 1.0 if value else 0.0
            # Special handling for focus (only when auto_focus is False)
            elif param_name == 'focus' and getattr(self, 'auto_focus', True) is False:
                props[cv2_prop] = float(value)
            # Other parameters direct conversion
            elif param_name != 'focus':  # focus already handled above
                props[cv2_prop] = float(value)

        return props

    def _ensure_mapper_ready(self, camera):
        """Ensure mapper is initialized"""
        if self._initialized:
            return

        # Use unified method to detect all normalized parameter ranges
        self.mapper.detect_all_ranges(camera)
        self._initialized = True

    def apply_to_camera(self, camera_capture: cv2.VideoCapture) -> Dict[str, Any]:
        """Apply camera settings to OpenCV VideoCapture object"""
        if not camera_capture.isOpened():
            raise ValidationError("Camera is not opened")

        # Ensure parameter mapper is initialized
        self._ensure_mapper_ready(camera_capture)

        results = {}
        opencv_props = self.get_opencv_properties()

        for cv2_prop, value in opencv_props.items():
            try:
                prop_name = OpenCVPropertyMapper.get_param_name(cv2_prop)

                # Check if normalization mapping is needed
                needs_mapping = OpenCVPropertyMapper.needs_normalization(prop_name)

                # Use mapper to convert normalized value to actual camera value
                camera_value = (self.mapper.normalize_to_camera(prop_name, value)
                                if needs_mapping else value)

                success = camera_capture.set(cv2_prop, camera_value)

                results[prop_name] = {
                    'success': success,
                    'requested': value,
                    'actual': camera_value,
                    'mapped': needs_mapping
                }

                if success:
                    logger.debug(f"Applied {prop_name} = {camera_value}"
                                 f"{' (mapped)' if needs_mapping else ''}")
                else:
                    logger.warning(f"Failed to apply {prop_name} = {camera_value}")

            except Exception as e:
                prop_name = OpenCVPropertyMapper.get_param_name(cv2_prop)
                results[prop_name] = {'success': False, 'error': str(e)}
                logger.error(f"Error applying {prop_name}: {e}")

        return results

    def reset_to_camera_defaults(self) -> Dict[str, Any]:
        """Reset all parameters to camera-detected defaults"""
        detector = CameraDefaultDetector(self.camera_id)
        detected_defaults = detector.detect_camera_defaults()

        changes = {}

        for field_name in self.__dataclass_fields__:
            if field_name in ['camera_id', 'output_dir']:
                continue

            old_value = getattr(self, field_name)
            new_value = detected_defaults.get(field_name)

            if new_value is not None:
                setattr(self, field_name, new_value)
                changes[field_name] = {'old': old_value, 'new': new_value}

        logger.info(f"Reset to camera defaults: {list(changes.keys())}")
        return {'changes': changes}

    def to_dict(self) -> Dict[str, Any]:
        """Convert camera model to dictionary"""
        result = {}
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if field_name == 'output_dir':
                result[field_name] = str(value)
            else:
                result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraParameterBase':
        """Create CameraParameterBase instance from dictionary"""
        # Filter out unknown keys
        valid_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        return cls(**filtered_data)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all camera settings"""
        summary = {'camera_id': self.camera_id, 'output_dir': str(self.output_dir)}

        # All parameters should have values now
        for field_name in self.__dataclass_fields__:
            if field_name in ['camera_id', 'output_dir']:
                continue
            value = getattr(self, field_name)
            if value is not None:
                summary[field_name] = value

        return summary

    def get_parameter_info(self) -> Dict[str, Dict[str, Any]]:
        """Get simplified parameter information"""
        info = {}

        for field_name, field_obj in self.__dataclass_fields__.items():
            field_type = field_obj.type
            metadata = field_obj.metadata.copy()

            info[field_name] = {
                "type": str(field_type),
                "current_value": getattr(self, field_name),
                "description": metadata.get("description", "No description available")
            }

        return info

    def __str__(self) -> str:
        """String representation showing all parameters"""
        params = []
        for key, value in self.get_summary().items():
            if key not in ['camera_id', 'output_dir'] and value is not None:
                params.append(f"{key}={value}")

        params_str = ', '.join(params) if params else 'all defaults'
        return f"CameraParameterBase(id={self.camera_id}, {params_str})"


@dataclass
class PhotoParameters(CameraParameterBase):
    """Parameters specific to photo capture - inherits auto-detection"""
    pass


@dataclass
class VideoParameters(CameraParameterBase):
    """Parameters specific to video recording - inherits auto-detection"""

    fps: Optional[float] = field(
        default=None,
        metadata={"description": "Frames per second (None = auto-detect)"}
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert video parameters to dictionary including fps"""
        result = super().to_dict()
        result['fps'] = self.fps
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoParameters':
        """Create VideoParameters instance from dictionary"""
        # Filter out unknown keys
        valid_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


# Convenience functions for common use cases
def create_auto_camera(camera_id: int = 0, output_dir: str = "output") -> CameraParameterBase:
    """Create camera with full auto-detection"""
    return CameraParameterBase(camera_id=camera_id, output_dir=output_dir)


def create_custom_camera(camera_id: int = 0, output_dir: str = "output", **custom_params) -> CameraParameterBase:
    """Create camera with custom parameters and auto-detection for others"""
    return CameraParameterBase(camera_id=camera_id, output_dir=output_dir, **custom_params)


if __name__ == '__main__':
    print("=== Simplified Camera Parameter Model ===")
    print(f"User: Gordon")
    print(f"Time: 2025-08-21 06:27:56")

    # Test full auto-detection
    print("\n1. Full auto-detection:")
    auto_camera = create_auto_camera()
    print(f"Auto camera: {auto_camera}")
    print(f"Summary: {auto_camera.get_summary()}")

    # Test partial customization
    print("\n2. Partial customization:")
    custom_camera = create_custom_camera(
        camera_id=0,
        brightness=0.3,  # Custom
        contrast=0.2,    # Custom
        # Others auto-detect
    )
    print(f"Custom camera: {custom_camera}")

    # Test parameter update
    print("\n3. Parameter update:")
    update_result = custom_camera.update_parameters(
        saturation=0.1,
        exposure=0.5
    )
    print(f"Update result: {update_result}")
    print(f"Updated camera: {custom_camera}")

    # Test reset to defaults
    print("\n4. Reset to camera defaults:")
    reset_result = custom_camera.reset_to_camera_defaults()
    print(f"Reset result: {reset_result}")