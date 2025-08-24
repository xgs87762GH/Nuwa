"""Camera service interface definitions with simplified validation."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable

from model.camera import PhotoParameters, VideoParameters


class ICameraService(ABC):
    """
    Interface for camera service with auto-detection and simplified validation.

    This interface defines all camera operations with intelligent parameter defaults
    and minimal validation requirements.
    """

    @abstractmethod
    def take_photo(
            self,
            filename: Optional[str] = None,
            quality: int = 95,
            photo_params: Optional[PhotoParameters] = None
    ) -> Dict[str, Any]:
        """
        Take photo with auto-detected defaults and optional parameter override.

        Args:
            filename: Custom filename (without extension). If None, auto-generated.
            quality: JPEG quality (1-100). Higher values mean better quality.
            photo_params: Temporary camera parameters for this photo only.
                         Parameters use auto-detection when None.

        Returns:
            Result dictionary containing:
            - status: "success" or "error"
            - file_path: Full path to saved image (on success)
            - filename: Name of saved file (on success)
            - file_size: Size of saved file in bytes (on success)
            - resolution: [width, height] of captured image (on success)
            - quality: JPEG quality used (on success)
            - camera_params: Summary of effective camera parameters (on success)
            - message: Error description (on error)

        Note:
            All camera parameters have intelligent defaults from auto-detection.
            No complex validation needed as defaults are always reasonable.
        """
        pass

    @abstractmethod
    def record_video(
            self,
            duration: int = 10,
            filename: Optional[str] = None,
            video_params: Optional[VideoParameters] = None,
            progress_callback: Optional[Callable[[float, Dict[str, Any]], None]] = None,
            codec_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record video with auto-detected defaults and dynamic parameters.

        Args:
            duration: Recording duration in seconds. Must be positive.
            filename: Custom filename (without extension). If None, auto-generated.
            video_params: Temporary camera parameters for this video only.
                         Parameters use auto-detection when None.
            progress_callback: Callback function called periodically during recording.
            codec_preference: Preferred video codec (e.g., 'H264', 'XVID').

        Returns:
            Result dictionary containing:
            - status: "success" or "error"
            - file_path: Full path to saved video (on success)
            - filename: Name of saved file (on success)
            - file_size: Size of saved file in bytes (on success)
            - duration: Actual recording duration (on success)
            - planned_duration: Requested duration (on success)
            - frames_written: Number of frames successfully written (on success)
            - total_frames: Total frames planned (on success)
            - fps: Recording FPS used (on success)
            - resolution: [width, height] of video (on success)
            - camera_params: Summary of effective camera parameters (on success)
            - message: Error description (on error)
        """
        pass

    @abstractmethod
    def update_camera_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Update camera parameters with minimal validation.

        Args:
            **kwargs: Parameters to update. All parameters accept reasonable values
                     due to auto-detection providing safe defaults.
                     Common parameters: brightness, contrast, saturation, hue,
                     gain, exposure, width, height, fps, auto_focus, focus.

        Returns:
            Update result dictionary containing:
            - changes: Dict of parameters that were changed
            - errors: Dict of parameters with basic validation errors (if any)
            - camera_test: Results of testing parameters with actual camera (if available)
            - actual_values: Camera's actual parameter values after setting (if available)
            - camera_test_error: Error message if camera testing failed (if applicable)

        Note:
            Validation is minimal - only checks camera_id and output_dir for basic requirements.
            Other parameters are trusted due to intelligent auto-detection defaults.
        """
        pass

    @abstractmethod
    def get_camera_info(self) -> Dict[str, Any]:
        """
        Get comprehensive camera information including auto-detected settings.

        Returns:
            Camera information dictionary containing:
            - status: "success" or "error"
            - camera_id: Camera identifier used (on success)
            - resolution: [width, height] current or auto-detected resolution (on success)
            - fps: Current or auto-detected frames per second (on success)
            - current_settings: Dict of current camera property values (on success)
            - model_config: Summary of effective camera model configuration (on success)
            - auto_detected_defaults: Dict of auto-detected default values (on success)
            - capture_test: Results of test frame capture (on success)
            - output_dir: Output directory path (on success)
            - message: Error description (on error)

        Note:
            Shows both user-configured and auto-detected parameter values.
            All parameters have reasonable defaults from camera detection.
        """
        pass

    @abstractmethod
    def test_camera(self) -> Dict[str, Any]:
        """
        Test camera availability and auto-detection capabilities.

        Returns:
            Test result dictionary containing:
            - status: "success", "warning", or "error"
            - available: Boolean indicating if camera can be opened
            - can_capture: Boolean indicating if frames can be captured
            - can_auto_detect: Boolean indicating if auto-detection works
            - resolution: [width, height] if capture successful
            - frame_channels: Number of color channels if capture successful
            - detected_defaults: Sample of auto-detected defaults (if available)
            - message: Additional information for warnings
            - error: Error description if camera unavailable
        """
        pass

    # @abstractmethod
    # def capture_preview(self, save_preview: bool = False) -> Dict[str, Any]:
    #     """
    #     Capture preview frame using effective camera parameters.
    #
    #     Args:
    #         save_preview: Whether to save preview image to disk.
    #
    #     Returns:
    #         Preview result dictionary containing:
    #         - status: "success" or "error"
    #         - resolution: [width, height] of captured frame (on success)
    #         - channels: Number of color channels (on success)
    #         - dtype: NumPy data type of frame (on success)
    #         - frame_size: Size of frame data in bytes (on success)
    #         - effective_params: Dict of effective parameters used (on success)
    #         - preview_path: Path to saved preview file (if save_preview=True)
    #         - preview_size: Size of saved preview file (if save_preview=True)
    #         - message: Error description (on error)
    #     """
    #     pass

    @abstractmethod
    def batch_photos(
            self,
            count: int,
            interval: float = 1.0,
            photo_params: Optional[PhotoParameters] = None,
            progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Capture multiple photos with consistent auto-detected or custom settings.

        Args:
            count: Number of photos to capture. Must be positive.
            interval: Interval between photos in seconds. Can be 0 for rapid capture.
            photo_params: Camera parameters for all photos in the batch.
                         Uses auto-detection for None values.
            progress_callback: Callback function called after each photo.

        Returns:
            Batch capture results dictionary containing:
            - status: "success" or "error"
            - total_requested: Number of photos requested
            - successful_captures: Number of photos successfully saved
            - failed_captures: Number of photos that failed
            - results: List of individual photo results with details
            - effective_params: Summary of effective camera parameters used
            - auto_detected_count: Number of parameters that were auto-detected
            - message: Error description (on error)
            - partial_results: Partial results if batch was interrupted (on error)
        """
        pass

    @abstractmethod
    def reset_to_camera_defaults(self) -> Dict[str, Any]:
        """
        Reset all parameters to camera-detected defaults.

        Returns:
            Reset results dictionary containing:
            - status: "success" or "error"
            - changes: Dict of parameters that were reset
            - auto_detected_defaults: Dict of new auto-detected values
            - detection_timestamp: When defaults were detected
            - message: Error description (on error)
        """
        pass




