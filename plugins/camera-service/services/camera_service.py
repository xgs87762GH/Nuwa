"""Camera service with dynamic parameter configuration - Optimized version."""

import logging
import sys
import time
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Any, Optional, Callable

import cv2

from interface.camera_interface import ICameraService
from core.exceptions import CameraServiceError
from model.camera import CameraParameterBase, PhotoParameters, VideoParameters
from utils.codec_utils import VideoCodecManager
from utils.media_writer import ImageWriter
from utils.file_path_manager import PathService

logger = logging.getLogger(__name__)

try:
    # 检查是否存在 DictValue 问题
    if hasattr(cv2, 'dnn') and not hasattr(cv2.dnn, 'DictValue'):
        # 为新版本 OpenCV 添加兼容性
        class DictValue:
            def __init__(self, value=None):
                self.value = value


        cv2.dnn.DictValue = DictValue
        print("Applied OpenCV compatibility patch")

except ImportError as e:
    print(f"Failed to import cv2: {e}")
    sys.exit(1)


class CameraService(ICameraService, ABC):
    """Camera service with dynamic configuration support - Optimized implementation."""

    def __init__(self, camera_model: CameraParameterBase = CameraParameterBase()):
        self.camera_model = camera_model
        self.path_service = PathService(camera_model.output_dir)
        self.image_writer = ImageWriter()
        self._current_camera: Optional[cv2.VideoCapture] = None
        self.codec_manager = VideoCodecManager('H264')

    @contextmanager
    def _get_camera(self, temp_params: Optional[CameraParameterBase] = None):
        """Context manager for camera operations with temporary parameters."""
        camera = None
        original_model = self.camera_model

        try:
            # Apply temporary parameters if provided
            if temp_params:
                self.camera_model = self._create_model_from_params(temp_params)

            # Open and configure camera
            camera = cv2.VideoCapture(self.camera_model.camera_id)
            if not camera.isOpened():
                raise CameraServiceError(f"Cannot open camera {self.camera_model.camera_id}")

            apply_results = self.camera_model.apply_to_camera(camera)
            logger.debug(f"Camera settings applied: {apply_results}")

            self._current_camera = camera
            yield camera

        finally:
            self._cleanup_camera(camera, original_model, temp_params)

    def _cleanup_camera(self, camera, original_model, temp_params):
        """Clean up camera resources and restore original model."""
        if camera:
            camera.release()
        self._current_camera = None
        if temp_params:
            self.camera_model = original_model

    def _create_model_from_params(self, params: CameraParameterBase) -> CameraParameterBase:
        """Create appropriate camera model from parameters."""
        if isinstance(params, VideoParameters):
            return VideoParameters.from_dict(params.to_dict())
        elif isinstance(params, PhotoParameters):
            return PhotoParameters.from_dict(params.to_dict())
        else:
            return CameraParameterBase.from_dict(params.to_dict())

    def _capture_frame(self, camera: cv2.VideoCapture) -> Any:
        """Capture a single frame from camera with error handling."""
        ret, frame = camera.read()
        if not ret or frame is None:
            raise CameraServiceError("Failed to capture frame")
        return frame

    def _get_frame_info(self, frame) -> Dict[str, Any]:
        """Extract common frame information."""
        height, width = frame.shape[:2]
        return {
            "resolution": [width, height],
            "channels": frame.shape[2] if len(frame.shape) > 2 else 1,
            "dtype": str(frame.dtype),
            "frame_size": frame.nbytes
        }

    def _save_image_with_info(self, frame, file_path: Path, quality: int = 95) -> Dict[str, Any]:
        """Save image and return file information."""
        if not self.image_writer.write_image(frame, file_path, quality):
            raise CameraServiceError(f"Failed to save image to {file_path}")

        file_size = file_path.stat().st_size
        frame_info = self._get_frame_info(frame)

        return {
            "file_path": str(file_path),
            "filename": file_path.name,
            "file_size": file_size,
            "quality": quality,
            **frame_info
        }

    def _merge_camera_params(self, base_params: CameraParameterBase,
                             override_params: CameraParameterBase) -> CameraParameterBase:
        """Merge camera parameters with override taking precedence."""
        merged_data = {**base_params.to_dict(), **{k: v for k, v in override_params.to_dict().items() if v is not None}}

        # Return the same type as override_params
        if isinstance(override_params, PhotoParameters):
            return PhotoParameters.from_dict(merged_data)
        elif isinstance(override_params, VideoParameters):
            return VideoParameters.from_dict(merged_data)
        else:
            return CameraParameterBase.from_dict(merged_data)

    def _get_effective_params(self, temp_params: Optional[CameraParameterBase],
                              param_type: type = CameraParameterBase) -> CameraParameterBase:
        """
        Get effective parameters by merging temp params with the current model.
        Handles dictionary inputs by converting them to the specified param_type.
        """
        if not temp_params:
            return self.camera_model

        # If temp_params is a dict, convert it to a model instance
        if isinstance(temp_params, dict):
            # Use the provided type hint to create the correct model
            if param_type is PhotoParameters:
                temp_params = PhotoParameters.from_dict(temp_params)
            elif param_type is VideoParameters:
                temp_params = VideoParameters.from_dict(temp_params)
            else:
                temp_params = CameraParameterBase.from_dict(temp_params)

        if hasattr(self, 'camera_model'):
            return self._merge_camera_params(self.camera_model, temp_params)

        return temp_params

    def take_photo(self, filename: Optional[str] = None, quality: int = 95,
                   photo_params: Optional[PhotoParameters] = None) -> Dict[str, Any]:
        """Take photo with auto-detected defaults and optional parameter override."""
        if not 1 <= quality <= 100:
            return {"status": "error", "message": "Quality must be 1-100"}

        try:
            effective_params = self._get_effective_params(photo_params, param_type=PhotoParameters)

            with self._get_camera(effective_params) as camera:
                frame = self._capture_frame(camera)
                file_path = self.path_service.generate_photo_path(filename)
                result = self._save_image_with_info(frame, file_path, quality)

                logger.info(f"Photo saved: {file_path} ({result['file_size']} bytes)")

                return {
                    "status": "success",
                    "camera_params": self.camera_model.get_summary(),
                    **result
                }

        except Exception as e:
            logger.error(f"Photo capture failed: {e}")
            return {"status": "error", "message": str(e)}

    def _record_video_frames(self, camera, video_writer, total_frames, recording_fps, progress_callback):
        """Record video frames with improved timing control to prevent frame skipping."""
        frames_written = 0
        frames_captured = 0
        start_time = time.time()

        # 计算每帧的时间间隔
        frame_interval = 1.0 / recording_fps

        logger.info(f"Recording: {total_frames} frames at {recording_fps}fps (interval: {frame_interval:.4f}s)")

        for frame_num in range(total_frames):
            frame_start_time = time.time()

            # 捕获帧
            ret, frame = camera.read()
            frames_captured += 1

            if ret and frame is not None:
                # 直接写入，不进行额外的条件检查
                success = video_writer.write(frame)
                if success:
                    frames_written += 1
                else:
                    logger.warning(f"Failed to write frame {frame_num}")
            else:
                logger.warning(f"Failed to capture frame {frame_num}")

            # 进度回调 - 降低调用频率以减少性能影响
            if progress_callback and frame_num % max(1, int(recording_fps // 2)) == 0:
                self._call_progress_callback(progress_callback, frame_num, total_frames, frames_written, start_time)

            # 改进的帧时序控制
            self._improved_frame_timing_control(frame_num, frame_interval, start_time, frame_start_time)

        logger.info(f"Recording completed: {frames_captured} captured, {frames_written} written")
        return frames_written

    def _improved_frame_timing_control(self, frame_num, frame_interval, start_time, frame_start_time):
        """Improved frame timing control to maintain consistent FPS."""
        # 计算应该经过的时间
        expected_elapsed = (frame_num + 1) * frame_interval
        actual_elapsed = time.time() - start_time

        # 如果我们太快了，等待
        if actual_elapsed < expected_elapsed:
            sleep_time = expected_elapsed - actual_elapsed
            # 限制最大睡眠时间，避免过度等待
            if sleep_time > 0 and sleep_time < frame_interval:
                time.sleep(sleep_time)

        # 如果我们太慢了，记录警告（但不跳帧）
        elif actual_elapsed > expected_elapsed + frame_interval:
            delay = actual_elapsed - expected_elapsed
            if frame_num % int(30) == 0:  # 每30帧记录一次，避免日志过多
                logger.debug(f"Frame {frame_num}: running {delay:.3f}s behind schedule")

    def record_video(self, duration: int = 10, filename: Optional[str] = None,
                     video_params: Optional[VideoParameters] = None,
                     progress_callback: Optional[Callable[[float, Dict[str, Any]], None]] = None,
                     codec_preference: Optional[str] = None) -> Dict[str, Any]:
        """Record video with improved frame timing to prevent skipping."""
        if duration <= 0:
            return {"status": "error", "message": "Duration must be positive"}

        # Use a more conservative default FPS to avoid frame skips
        recording_fps = (isinstance(self.camera_model, VideoParameters) and self.camera_model.fps) or 25.0

        try:
            effective_params = self._get_effective_params(video_params, param_type=VideoParameters)
            if isinstance(effective_params, VideoParameters):
                effective_params.fps = recording_fps

            with self._get_camera(effective_params) as camera:
                # Warm up camera - read a few frames to stabilize camera
                logger.debug("Warming up camera...")
                for _ in range(3):
                    camera.read()
                    time.sleep(0.1)

                frame = self._capture_frame(camera)
                height, width = frame.shape[:2]
                file_path = self.path_service.generate_video_path(filename)
                total_frames = int(recording_fps * duration)

                # Set camera buffer size (if supported)
                try:
                    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                except:
                    pass  # Some camera drivers don't support this

                video_writer, codec_info = self.codec_manager.create_video_writer(
                    file_path=file_path, fps=recording_fps, frame_size=(width, height), preferred_codec=codec_preference
                )

                actual_file_path = Path(codec_info['file_path'])
                if not video_writer or not video_writer.isOpened():
                    raise CameraServiceError("No working video codec found")

                logger.info(f"Starting video recording: {duration}s at {recording_fps}fps ({total_frames} frames)")

                start_time = time.time()
                frames_written = self._record_video_frames(camera, video_writer, total_frames, recording_fps,
                                                           progress_callback)
                actual_duration = time.time() - start_time

                # Ensure video_writer is properly closed
                video_writer.release()

                file_size = actual_file_path.stat().st_size

                logger.info(
                    f"Video saved: {actual_file_path} ({frames_written}/{total_frames} frames, {file_size} bytes)")

                return {
                    "status": "success",
                    "file_path": str(actual_file_path),
                    "filename": actual_file_path.name,
                    "file_size": file_size,
                    "duration": actual_duration,
                    "planned_duration": duration,
                    "frames_written": frames_written,
                    "total_frames": total_frames,
                    "fps": recording_fps,
                    "resolution": [width, height],
                    "camera_params": self.camera_model.get_summary(),
                    "frame_efficiency": f"{frames_written}/{total_frames} ({frames_written / total_frames * 100:.1f}%)"
                }

        except Exception as e:
            logger.exception(e)
            logger.error(f"Video recording failed: {e}")
            return {"status": "error", "message": str(e)}

    def _record_video_frames(self, camera, video_writer, total_frames, recording_fps, progress_callback):
        """Record video frames with progress tracking."""
        frames_written = 0
        start_time = time.time()

        logger.info(f"Recording: {total_frames} frames at {recording_fps}fps")

        for frame_num in range(total_frames):
            ret, frame = camera.read()
            if ret and frame is not None and video_writer.write(frame):
                frames_written += 1

            # Progress callback
            if progress_callback and frame_num % int(recording_fps) == 0:
                self._call_progress_callback(progress_callback, frame_num, total_frames, frames_written, start_time)

            # Frame timing control
            self._control_frame_timing(frame_num, recording_fps, start_time)

        return frames_written

    def _call_progress_callback(self, progress_callback, frame_num, total_frames, frames_written, start_time):
        """Call progress callback with detailed information."""
        progress = (frame_num + 1) / total_frames
        elapsed = time.time() - start_time
        remaining = (elapsed / progress) - elapsed if progress > 0 else 0

        progress_info = {
            "progress": progress,
            "elapsed_time": elapsed,
            "remaining_time": remaining,
            "frames_written": frames_written,
            "current_frame": frame_num + 1,
            "total_frames": total_frames
        }
        progress_callback(progress, progress_info)

    def _control_frame_timing(self, frame_num, recording_fps, start_time):
        """Control frame timing to maintain proper FPS."""
        elapsed = time.time() - start_time
        expected_time = (frame_num + 1) / recording_fps
        if elapsed < expected_time:
            time.sleep(expected_time - elapsed)

    def update_camera_parameters(self, **kwargs) -> Dict[str, Any]:
        """Update camera parameters with minimal validation."""
        try:
            result = self.camera_model.update_parameters(**kwargs)

            if result.get('changes'):
                self._test_camera_parameters(result)

            return result

        except Exception as e:
            logger.error(f"Failed to update parameters: {e}")
            return {"status": "error", "message": str(e)}

    def _test_camera_parameters(self, result):
        """Test updated parameters with actual camera."""
        try:
            with self._get_camera() as camera:
                test_results = self.camera_model.apply_to_camera(camera)
                result['camera_test'] = test_results

                # Get actual camera values
                actual_values = self._get_actual_camera_values(camera, result['changes'])
                if actual_values:
                    result['actual_values'] = actual_values

        except Exception as e:
            result['camera_test_error'] = str(e)
            logger.warning(f"Could not test parameters with camera: {e}")

    def _get_actual_camera_values(self, camera, changed_params):
        """Get actual camera values for changed parameters."""
        from utils.camera_param_mapper import OpenCVPropertyMapper

        actual_values = {}
        opencv_props = self.camera_model.get_opencv_properties()

        for cv2_prop, value in opencv_props.items():
            param_name = OpenCVPropertyMapper.get_param_name(cv2_prop)
            if param_name in changed_params:
                actual_values[param_name] = camera.get(cv2_prop)

        return actual_values

    def get_camera_info(self) -> Dict[str, Any]:
        """Get comprehensive camera information."""
        try:
            with self._get_camera() as camera:
                frame = self._capture_frame(camera)

                return {
                    "status": "success",
                    "camera_id": self.camera_model.camera_id,
                    "resolution": [int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                   int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))],
                    "fps": camera.get(cv2.CAP_PROP_FPS),
                    "current_settings": self._get_current_camera_settings(camera),
                    "model_config": self.camera_model.get_summary(),
                    "capture_test": {"can_capture": True, "frame_shape": frame.shape},
                    "output_dir": str(self.camera_model.output_dir)
                }

        except Exception as e:
            logger.error(f"Failed to get camera info: {e}")
            return {"status": "error", "message": str(e)}

    def _get_current_camera_settings(self, camera):
        """Get current camera settings."""
        return {
            'brightness': camera.get(cv2.CAP_PROP_BRIGHTNESS),
            'contrast': camera.get(cv2.CAP_PROP_CONTRAST),
            'saturation': camera.get(cv2.CAP_PROP_SATURATION),
            'hue': camera.get(cv2.CAP_PROP_HUE),
            'gain': camera.get(cv2.CAP_PROP_GAIN),
            'exposure': camera.get(cv2.CAP_PROP_EXPOSURE),
        }

    def test_camera(self) -> Dict[str, Any]:
        """Test camera availability and basic functionality."""
        try:
            with self._get_camera() as camera:
                frame = self._capture_frame(camera)
                frame_info = self._get_frame_info(frame)

                return {
                    "status": "success",
                    "available": True,
                    "can_capture": True,
                    **frame_info
                }

        except Exception as e:
            return {"status": "error", "available": False, "can_capture": False, "error": str(e)}

    # def capture_preview(self, save_preview: bool = False) -> Dict[str, Any]:
    #     """Capture preview frame using effective camera parameters."""
    #     try:
    #         with self._get_camera() as camera:
    #             frame = self._capture_frame(camera)
    #             result = {"status": "success", **self._get_frame_info(frame)}
    #
    #             if save_preview:
    #                 preview_path = self.path_service.generate_photo_path("preview")
    #                 if self.image_writer.write_image(frame, preview_path, 90):
    #                     result.update({
    #                         "preview_path": str(preview_path),
    #                         "preview_size": preview_path.stat().st_size
    #                     })
    #
    #             return result
    #
    #     except Exception as e:
    #         logger_handler.error(f"Preview capture failed: {e}")
    #         return {"status": "error", "message": str(e)}

    def batch_photos(self, count: int, interval: float = 1.0, photo_params: Optional[PhotoParameters] = None,
                     progress_callback: Optional[Callable[[int, int], None]] = None) -> Dict[str, Any]:
        """Capture multiple photos with consistent settings."""
        if count <= 0:
            return {"status": "error", "message": "Count must be positive"}

        try:
            effective_params = self._get_effective_params(photo_params)
            results = []

            with self._get_camera(effective_params) as camera:
                for i in range(count):
                    result = self._capture_batch_photo(camera, i)
                    results.append(result)

                    if progress_callback:
                        progress_callback(i + 1, count)

                    if i < count - 1 and interval > 0:
                        time.sleep(interval)

            successful = sum(1 for r in results if r["status"] == "success")

            return {
                "status": "success",
                "total_requested": count,
                "successful_captures": successful,
                "failed_captures": count - successful,
                "results": results,
                "camera_params": self.camera_model.get_summary()
            }

        except Exception as e:
            logger.error(f"Batch photo capture failed: {e}")
            return {"status": "error", "message": str(e)}

    def _capture_batch_photo(self, camera, index):
        """Capture a single photo in batch operation."""
        try:
            frame = self._capture_frame(camera)
            timestamp = int(time.time() * 1000)
            filename = f"batch_{timestamp}_{index:03d}"
            file_path = self.path_service.generate_photo_path(filename)

            if self.image_writer.write_image(frame, file_path, 95):
                file_size = file_path.stat().st_size
                frame_info = self._get_frame_info(frame)

                return {
                    "index": index,
                    "status": "success",
                    "file_path": str(file_path),
                    "file_size": file_size,
                    **frame_info
                }
            else:
                return {"index": index, "status": "error", "message": "Failed to save image"}

        except Exception:
            return {"index": index, "status": "error", "message": "Failed to capture frame"}

    def reset_to_camera_defaults(self) -> Dict[str, Any]:
        """Reset all parameters to camera-detected defaults."""
        try:
            from datetime import datetime

            reset_result = self.camera_model.reset_to_camera_defaults()
            reset_result.update({
                "status": "success",
                "detection_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "service_user": "Gordon"
            })

            logger.info(f"Camera parameters reset to defaults for camera {self.camera_model.camera_id}")
            return reset_result

        except Exception as e:
            logger.error(f"Failed to reset camera defaults: {e}")
            return {"status": "error", "message": str(e)}
