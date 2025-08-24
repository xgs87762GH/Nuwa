from pathlib import Path
from typing import Union, Optional, List

import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ImageWriter:

    def __init__(self):
        pass

    def write_image(
            self,
            frame: np.ndarray,
            file_path: Union[str, Path],
            param: Optional[int] = None
    ) -> bool:
        """
        Write image frame to file with compression parameters.

        Args:
            frame: Image frame (numpy array)
            file_path: Output file path
            param: OpenCV compression parameters (e.g., [cv2.IMWRITE_JPEG_QUALITY, 95])

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to Path object
            if isinstance(file_path, str):
                file_path = Path(file_path)

            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Set default parameters if none provided
            cv2_params = None

            if param is None:
                ext = file_path.suffix.lower()
                if ext in ['.jpg', '.jpeg']:
                    cv2_params = [cv2.IMWRITE_JPEG_QUALITY, 95]
                elif ext == '.png':
                    cv2_params = [cv2.IMWRITE_PNG_COMPRESSION, 6]  # 0-9, 6 is good balance
                elif ext == '.webp':
                    cv2_params = [cv2.IMWRITE_WEBP_QUALITY, 95]
                else:
                    cv2_params = []  # Use default for other formats
            else:
                cv2_params = self._convert_quality_to_cv2_params(file_path, param)
            # Write image
            success = cv2.imwrite(str(file_path), frame, cv2_params)

            if success:
                logger.debug(f"Image saved: {file_path}")
            else:
                logger.error(f"Failed to save image: {file_path}")

            return success

        except Exception as e:
            logger.error(f"Error writing image to {file_path}: {e}")
            return False

    def _convert_quality_to_cv2_params(self, file_path, quality: int) -> Optional[list]:
        """
        Convert quality integer to OpenCV parameter format.

        Args:
            file_path: Output file path (used to determine format)
            quality: Quality value 1-100

        Returns:
            OpenCV parameters list or None
        """
        from pathlib import Path

        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        if ext in ['.jpg', '.jpeg']:
            return [cv2.IMWRITE_JPEG_QUALITY, quality]
        elif ext == '.png':
            # PNG compression: 0-9, convert quality (1-100) to compression (0-9)
            compression = max(0, min(9, (100 - quality) // 10))
            return [cv2.IMWRITE_PNG_COMPRESSION, compression]
        elif ext == '.webp':
            return [cv2.IMWRITE_WEBP_QUALITY, quality]
        else:
            # For other formats, let ImageWriter handle default parameters
            return None