"""
Completely isolated unit tests for ICameraService interface.
All camera operations are mocked to avoid real hardware dependencies.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any

# Import the service
from services.camera_service import CameraService


class TestCameraServiceIsolated(unittest.TestCase):
    """Completely isolated tests with all dependencies mocked."""

    def setUp(self):
        """Set up test fixtures with all dependencies mocked."""
        # Create mock camera model that behaves predictably
        self.mock_camera_model = Mock()
        self.mock_camera_model.camera_id = 0
        self.mock_camera_model.output_dir = Path("/tmp/test")
        self.mock_camera_model.fps = 30.0

        # Mock all camera model methods to avoid real operations
        self.mock_camera_model.apply_to_camera.return_value = {'status': 'success', 'applied': True}
        self.mock_camera_model.get_summary.return_value = {'fps': 30.0, 'camera_id': 0}
        self.mock_camera_model.to_dict.return_value = {
            'camera_id': 0, 'fps': 30.0, 'brightness': 0.5
        }
        self.mock_camera_model.update_parameters.return_value = {
            'changes': {'brightness': {'old': 0.5, 'new': 0.8}},
            'errors': {}
        }
        self.mock_camera_model.reset_to_camera_defaults.return_value = {
            'changes': {'brightness': {'old': 0.8, 'new': 0.5}},
            'auto_detected_defaults': {'brightness': 0.5}
        }
        self.mock_camera_model.get_opencv_properties.return_value = {cv2.CAP_PROP_BRIGHTNESS: 0.5}

        # Mock all service dependencies
        with patch('services.camera_service.PathService') as mock_path_service, \
             patch('services.camera_service.ImageWriter') as mock_image_writer, \
             patch('services.camera_service.VideoCodecManager') as mock_codec_manager:

            self.camera_service = CameraService(self.mock_camera_model)
            self.mock_path_service = mock_path_service.return_value
            self.mock_image_writer = mock_image_writer.return_value
            self.mock_codec_manager = mock_codec_manager.return_value

    def _create_mock_camera(self):
        """Create a properly configured mock camera."""
        mock_camera = Mock()
        mock_camera.isOpened.return_value = True
        mock_camera.set.return_value = True
        mock_camera.release.return_value = None

        # Create realistic frame data
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_camera.read.return_value = (True, mock_frame)

        # Mock camera property getter
        def mock_get(prop):
            return {
                cv2.CAP_PROP_FRAME_WIDTH: 640.0,
                cv2.CAP_PROP_FRAME_HEIGHT: 480.0,
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_BRIGHTNESS: 0.5,
                cv2.CAP_PROP_CONTRAST: 0.5,
                cv2.CAP_PROP_SATURATION: 0.5,
                cv2.CAP_PROP_HUE: 0.0,
                cv2.CAP_PROP_GAIN: 1.0,
                cv2.CAP_PROP_EXPOSURE: -5.0
            }.get(prop, 0.0)

        mock_camera.get.side_effect = mock_get
        return mock_camera

    def _create_mock_video_writer(self):
        """创建正确配置的mock视频写入器"""
        mock_video_writer = Mock()
        mock_video_writer.isOpened.return_value = True  # 关键：确保返回True
        mock_video_writer.write.return_value = True
        mock_video_writer.release.return_value = None
        return mock_video_writer


    @patch('cv2.VideoCapture')
    def test_take_photo_success(self, mock_video_capture):
        """Test successful photo capture."""
        # Setup mocks
        mock_camera = self._create_mock_camera()
        mock_video_capture.return_value = mock_camera

        mock_file_path = Mock(spec=Path)
        mock_file_path.stat.return_value = Mock(st_size=1024)
        mock_file_path.name = "test_photo.jpg"

        self.mock_path_service.generate_photo_path.return_value = mock_file_path
        self.mock_image_writer.write_image.return_value = True

        # Execute test
        result = self.camera_service.take_photo(quality=90)

        # Assertions
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["quality"], 90)
        self.assertEqual(result["resolution"], [640, 480])
        self.assertEqual(result["file_size"], 1024)
        self.assertIn("camera_params", result)

    def test_take_photo_invalid_quality(self):
        """Test photo capture with invalid quality."""
        result = self.camera_service.take_photo(quality=150)

        self.assertEqual(result["status"], "error")
        self.assertIn("Quality must be 1-100", result["message"])

    @patch('cv2.VideoCapture')
    def test_take_photo_camera_failure(self, mock_video_capture):
        """Test photo capture when camera fails to open."""
        mock_camera = Mock()
        mock_camera.isOpened.return_value = False
        mock_video_capture.return_value = mock_camera

        result = self.camera_service.take_photo()

        self.assertEqual(result["status"], "error")
        self.assertIn("Cannot open camera", result["message"])

    # @patch('cv2.VideoCapture')
    # @patch('time.time')
    # @patch('time.sleep')
    # def test_record_video_success(self, mock_sleep, mock_time, mock_video_capture):
    #     """Test successful video recording."""
    #     # Setup time sequence
    #     mock_time.side_effect = [1000.0, 1001.0, 1002.0]
    #
    #     # Setup camera
    #     mock_camera = self._create_mock_camera()
    #     mock_video_capture.return_value = mock_camera
    #
    #     # Setup video writer
    #     mock_video_writer = Mock()
    #     mock_video_writer.isOpened.return_value = True
    #     mock_video_writer.write.return_value = True
    #     mock_video_writer.release.return_value = None
    #
    #     mock_codec_info = {'file_path': '/tmp/test_video.mp4'}
    #     self.mock_codec_manager.create_video_writer.return_value = (mock_video_writer, mock_codec_info)
    #
    #     mock_file_path = Mock(spec=Path)
    #     mock_file_path.stat.return_value = Mock(st_size=4096)
    #     self.mock_path_service.generate_video_path.return_value = Path('/tmp/progress_video.mp4')
    #
    #     progress_calls = []
    #     def progress_callback(progress, info):
    #         progress_calls.append((progress, info))
    #     with patch.object(self.camera_service, '_record_video_frames') as mock_record_frames, \
    #             patch('pathlib.Path', return_value=mock_file_path):
    #         def mock_record_with_progress(camera, video_writer, total_frames, fps, callback):
    #             # Simulate calling progress callback during recording
    #             if callback:
    #                 callback(0.25, {"frames_written": total_frames // 4, "elapsed": 0.25})
    #                 callback(0.50, {"frames_written": total_frames // 2, "elapsed": 0.50})
    #                 callback(0.75, {"frames_written": total_frames * 3 // 4, "elapsed": 0.75})
    #                 callback(1.00, {"frames_written": total_frames, "elapsed": 1.00})
    #             return total_frames
    #
    #         mock_record_frames.side_effect = mock_record_with_progress
    #
    #         result = self.camera_service.record_video(
    #             duration=1,
    #             progress_callback=progress_callback
    #         )
    #
    #     # Setup file path
    #     mock_file_path = Mock(spec=Path)
    #     mock_file_path.stat.return_value = Mock(st_size=5120)
    #     mock_file_path.name = "test_video.mp4"
    #
    #     self.mock_path_service.generate_video_path.return_value = Path('/tmp/test_video.mp4')
    #
    #     with patch('pathlib.Path', return_value=mock_file_path):
    #         result = self.camera_service.record_video(duration=2)
    #
    #     # Assertions
    #     self.assertEqual(result["status"], "success")
    #     self.assertEqual(result["planned_duration"], 2)
    #     self.assertEqual(result["fps"], 25.0)  # Conservative default
    #     self.assertEqual(result["resolution"], [640, 480])

    def test_record_video_invalid_duration(self):
        """Test video recording with invalid duration."""
        result = self.camera_service.record_video(duration=-1)

        self.assertEqual(result["status"], "error")
        self.assertIn("Duration must be positive", result["message"])

    @patch('cv2.VideoCapture')
    def test_record_video_no_codec(self, mock_video_capture):
        """Test video recording when no codec is available."""
        mock_camera = self._create_mock_camera()
        mock_video_capture.return_value = mock_camera

        # No working video writer
        mock_codec_info = {'file_path': '/tmp/test.mp4'}
        self.mock_codec_manager.create_video_writer.return_value = (None, mock_codec_info)

        result = self.camera_service.record_video(duration=1)

        self.assertEqual(result["status"], "error")
        self.assertIn("No working video codec found", result["message"])

    def test_update_camera_parameters_success(self):
        """Test successful parameter update."""
        result = self.camera_service.update_camera_parameters(brightness=0.8)

        self.assertIn('changes', result)
        self.mock_camera_model.update_parameters.assert_called_once_with(brightness=0.8)

    @patch('cv2.VideoCapture')
    def test_update_camera_parameters_with_testing(self, mock_video_capture):
        """Test parameter update with camera testing."""
        mock_camera = self._create_mock_camera()
        mock_video_capture.return_value = mock_camera

        # Configure mock to return changes
        self.mock_camera_model.update_parameters.return_value = {
            'changes': {'brightness': {'old': 0.5, 'new': 0.8}}
        }

        with patch('utils.camera_mapper.OpenCVPropertyMapper.get_param_name', return_value='brightness'):
            result = self.camera_service.update_camera_parameters(brightness=0.8)

            self.assertIn('camera_test', result)

    @patch('cv2.VideoCapture')
    def test_get_camera_info_success(self, mock_video_capture):
        """Test successful camera info retrieval."""
        mock_camera = self._create_mock_camera()
        mock_video_capture.return_value = mock_camera

        result = self.camera_service.get_camera_info()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["camera_id"], 0)
        self.assertEqual(result["resolution"], [640, 480])
        self.assertEqual(result["fps"], 30.0)
        self.assertIn("current_settings", result)

    @patch('cv2.VideoCapture')
    def test_test_camera_success(self, mock_video_capture):
        """Test successful camera test."""
        mock_camera = self._create_mock_camera()
        mock_video_capture.return_value = mock_camera

        result = self.camera_service.test_camera()

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["available"])
        self.assertTrue(result["can_capture"])
        self.assertEqual(result["resolution"], [640, 480])

    @patch('cv2.VideoCapture')
    def test_test_camera_unavailable(self, mock_video_capture):
        """Test camera test when unavailable."""
        mock_camera = Mock()
        mock_camera.isOpened.return_value = False
        mock_video_capture.return_value = mock_camera

        result = self.camera_service.test_camera()

        self.assertEqual(result["status"], "error")
        self.assertFalse(result["available"])

    @patch('cv2.VideoCapture')
    def test_capture_preview_success(self, mock_video_capture):
        """Test successful preview capture."""
        mock_camera = self._create_mock_camera()
        mock_video_capture.return_value = mock_camera

        result = self.camera_service.capture_preview()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["resolution"], [640, 480])
        self.assertEqual(result["channels"], 3)

    @patch('cv2.VideoCapture')
    def test_capture_preview_with_save(self, mock_video_capture):
        """Test preview capture with save option."""
        mock_camera = self._create_mock_camera()
        mock_video_capture.return_value = mock_camera

        mock_preview_path = Mock(spec=Path)
        mock_preview_path.stat.return_value = Mock(st_size=15360)

        self.mock_path_service.generate_photo_path.return_value = mock_preview_path
        self.mock_image_writer.write_image.return_value = True

        result = self.camera_service.capture_preview(save_preview=True)

        self.assertEqual(result["status"], "success")
        self.assertIn("preview_path", result)
        self.assertEqual(result["preview_size"], 15360)

    @patch('cv2.VideoCapture')
    @patch('time.time')
    @patch('time.sleep')
    def test_batch_photos_success(self, mock_sleep, mock_time, mock_video_capture):
        """Test successful batch photo capture."""
        # Mock time for filename generation
        mock_time.side_effect = [1000000, 1001000, 1002000, 1003000]

        mock_camera = self._create_mock_camera()
        mock_video_capture.return_value = mock_camera

        # Mock file operations for each photo
        mock_file_paths = []
        for i in range(3):
            mock_path = Mock(spec=Path)
            mock_path.stat.return_value = Mock(st_size=1024 * (i + 1))
            mock_file_paths.append(mock_path)

        self.mock_path_service.generate_photo_path.side_effect = mock_file_paths
        self.mock_image_writer.write_image.return_value = True

        progress_calls = []
        def progress_callback(current, total):
            progress_calls.append((current, total))

        result = self.camera_service.batch_photos(
            count=3,
            interval=0.5,
            progress_callback=progress_callback
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_requested"], 3)
        self.assertEqual(result["successful_captures"], 3)
        self.assertEqual(result["failed_captures"], 0)
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(progress_calls, [(1, 3), (2, 3), (3, 3)])

    def test_batch_photos_invalid_count(self):
        """Test batch photos with invalid count."""
        result = self.camera_service.batch_photos(count=0)

        self.assertEqual(result["status"], "error")
        self.assertIn("Count must be positive", result["message"])

    @patch('datetime.datetime')
    def test_reset_to_camera_defaults_success(self, mock_datetime):
        """Test successful reset to defaults."""
        mock_datetime.utcnow.return_value.strftime.return_value = "2025-08-21 07:20:04"

        result = self.camera_service.reset_to_camera_defaults()

        self.assertEqual(result["status"], "success")
        self.assertIn("changes", result)
        self.assertEqual(result["detection_timestamp"], "2025-08-21 07:20:04")
        self.assertEqual(result["service_user"], "Gordon")

    @patch('datetime.datetime')
    def test_reset_to_camera_defaults_failure(self, mock_datetime):
        """Test reset failure."""
        mock_datetime.utcnow.return_value.strftime.return_value = "2025-08-21 07:20:04"
        self.mock_camera_model.reset_to_camera_defaults.side_effect = Exception("Reset failed")

        result = self.camera_service.reset_to_camera_defaults()

        self.assertEqual(result["status"], "error")
        self.assertIn("Reset failed", result["message"])


class TestCameraServiceWithCustomParams(unittest.TestCase):
    """Test camera service with custom parameter objects."""

    def setUp(self):
        """Setup with mock camera model."""
        self.mock_camera_model = Mock()
        self.mock_camera_model.camera_id = 0
        self.mock_camera_model.output_dir = Path("/tmp/test")
        self.mock_camera_model.apply_to_camera.return_value = {'status': 'success'}
        self.mock_camera_model.get_summary.return_value = {'fps': 30.0}

        with patch('services.camera_service.PathService'), \
             patch('services.camera_service.ImageWriter'), \
             patch('services.camera_service.VideoCodecManager'):
            self.camera_service = CameraService(self.mock_camera_model)

    # @patch('cv2.VideoCapture')
    # def test_take_photo_with_photo_parameters(self, mock_video_capture):
    #     """Test photo capture with PhotoParameters."""
    #     mock_camera = Mock()
    #     mock_camera.isOpened.return_value = True
    #     mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    #     mock_camera.read.return_value = (True, mock_frame)
    #     mock_video_capture.return_value = mock_camera
    #
    #     # Mock PhotoParameters
    #     mock_photo_params = Mock()
    #     mock_photo_params.to_dict.return_value = {'brightness': 0.8, 'contrast': 0.6}
    #     mock_photo_params.apply_to_camera.return_value = {'applied': True}
    #     mock_photo_params.get_summary.return_value = {'brightness': 0.8}
    #
    #     mock_file_path = Mock(spec=Path)
    #     mock_file_path.stat.return_value = Mock(st_size=2048)
    #     mock_file_path.name = "custom_photo.jpg"
    #
    #     with patch.object(self.camera_service.path_service, 'generate_photo_path', return_value=mock_file_path), \
    #          patch.object(self.camera_service.image_writer, 'write_image', return_value=True), \
    #          patch('core.model.camera.PhotoParameters.from_dict', return_value=mock_photo_params):
    #
    #         result = self.camera_service.take_photo(photo_params=mock_photo_params)
    #
    #         self.assertEqual(result["status"], "success")


if __name__ == '__main__':
    # Disable logging to reduce noise
    import logging
    logging.disable(logging.CRITICAL)

    # Run tests
    unittest.main(verbosity=2)