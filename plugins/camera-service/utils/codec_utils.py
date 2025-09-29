"""Video codec manager for handling multiple encoding formats with fallback support."""

import logging
import cv2
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from core import getCodecs, CameraServiceError

logger = logging.getLogger(__name__)

CODEC_CONFIGS = getCodecs()


class VideoCodecManager:
    """Manages video codecs with automatic fallback support."""

    def __init__(self, preferred_codec: Optional[str] = None):
        """
        Initialize codec manager.

        Args:
            preferred_codec: Preferred codec name (e.g., 'H264', 'XVID')
        """
        self.preferred_codec = preferred_codec
        self.tested_codecs: Dict[str, bool] = {}

    def get_available_codecs(self) -> List[Dict[str, Any]]:
        """Get list of available codecs on current system."""
        available = []

        for codec_config in CODEC_CONFIGS:
            codec_name = codec_config['name']
            if self._test_codec_support(codec_config):
                available.append(codec_config)
                self.tested_codecs[codec_name] = True
                logger.debug(f"Codec {codec_name} is available")
            else:
                self.tested_codecs[codec_name] = False
                logger.debug(f"Codec {codec_name} is not available")

        return available

    def _test_codec_support(self, codec_config: Dict[str, Any]) -> bool:
        """Test if a codec is supported on the current system."""
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec_config['fourcc'])
            # 尝试创建一个临时的 VideoWriter 来测试编码器支持
            test_writer = cv2.VideoWriter()
            # 使用一个临时文件路径进行测试
            temp_path = f"test_{codec_config['name']}{codec_config['extension']}"

            # 尝试初始化（不实际创建文件）
            result = test_writer.open(temp_path, fourcc, 30.0, (640, 480))
            test_writer.release()

            # 删除可能创建的测试文件
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass

            return result

        except Exception as e:
            logger.debug(f"Codec {codec_config['name']} test failed: {e}")
            return False

    def create_video_writer(
            self,
            file_path: Path,
            fps: float,
            frame_size: Tuple[int, int],
            preferred_codec: Optional[str] = None
    ) -> Tuple[cv2.VideoWriter, Dict[str, Any]]:
        """
        Create a VideoWriter with automatic codec fallback.

        Args:
            file_path: Output file path
            fps: Frames per second
            frame_size: (width, height) tuple
            preferred_codec: Override preferred codec for this call

        Returns:
            Tuple of (VideoWriter object, codec_info dict)

        Raises:
            CameraServiceError: If no working codec found
        """
        # 确定编码器优先级
        codec_priority = self._get_codec_priority(preferred_codec)

        last_error = None

        for codec_config in codec_priority:
            try:
                # 调整文件扩展名
                adjusted_path = self._adjust_file_extension(file_path, codec_config)

                # 创建 VideoWriter
                fourcc = cv2.VideoWriter_fourcc(*codec_config['fourcc'])
                video_writer = cv2.VideoWriter(
                    str(adjusted_path),
                    fourcc,
                    fps,
                    frame_size
                )

                # 测试是否成功初始化
                if video_writer.isOpened():
                    codec_info = {
                        'codec_name': codec_config['name'],
                        'fourcc': codec_config['fourcc'],
                        'file_path': str(adjusted_path),
                        'extension': codec_config['extension'],
                        'description': codec_config['description']
                    }

                    logger.info(f"Video writer initialized with {codec_config['name']} codec")
                    return video_writer, codec_info
                else:
                    video_writer.release()
                    last_error = f"Failed to open VideoWriter with {codec_config['name']}"
                    logger.warning(last_error)

            except Exception as e:
                last_error = f"Error with {codec_config['name']} codec: {str(e)}"
                logger.warning(last_error)
                continue

        # 如果所有编码器都失败了
        available_codecs = [c['name'] for c in self.get_available_codecs()]
        error_msg = f"No working video codec found. Available codecs: {available_codecs}. Last error: {last_error}"
        raise CameraServiceError(error_msg)

    def _get_codec_priority(self, preferred_codec: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get codec priority list based on preferences."""
        # 使用传入的首选编码器或实例首选编码器
        target_codec = preferred_codec or self.preferred_codec

        if target_codec:
            # 查找首选编码器配置
            preferred_config = None
            remaining_configs = []

            for config in CODEC_CONFIGS:
                if config['name'].upper() == target_codec.upper():
                    preferred_config = config
                else:
                    remaining_configs.append(config)

            # 如果找到首选编码器，将其放在第一位
            if preferred_config:
                return [preferred_config] + remaining_configs

        # 使用默认顺序
        return CODEC_CONFIGS.copy()

    def _adjust_file_extension(self, file_path: Path, codec_config: Dict[str, Any]) -> Path:
        """Adjust file extension based on codec."""
        new_extension = codec_config['extension']

        # 如果当前扩展名与编码器推荐的不同，则更改
        if file_path.suffix.lower() != new_extension.lower():
            new_path = file_path.with_suffix(new_extension)
            logger.debug(f"Adjusted file extension from {file_path.suffix} to {new_extension}")
            return new_path

        return file_path

    def get_codec_info(self) -> Dict[str, Any]:
        """Get information about available codecs."""
        available_codecs = self.get_available_codecs()

        return {
            'total_codecs': len(CODEC_CONFIGS),
            'available_codecs': len(available_codecs),
            'supported_codecs': [c['name'] for c in available_codecs],
            'codec_details': available_codecs,
            'preferred_codec': self.preferred_codec,
            'tested_codecs': self.tested_codecs
        }
