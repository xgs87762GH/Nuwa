import os

"""Path management service."""

import datetime
from pathlib import Path
from typing import Optional


def _get_default_base_dir() -> Path:
    """
    Get default base directory based on operating system.

    Returns:
        Default base directory path
    """
    # Get user home directory
    home_dir = Path.home()

    # Create camera-specific directory in user's directory
    if os.name == 'nt':  # Windows
        # Use Pictures folder on Windows
        pictures_dir = home_dir / "Pictures"
        if pictures_dir.exists():
            return pictures_dir / "CameraCaptures"
        else:
            return home_dir / "CameraCaptures"

    else:  # Linux/macOS
        # Use user home directory
        return home_dir / "CameraCaptures"


class PathService:
    """Service for managing file paths."""

    def __init__(self, base_dir: Optional[Path] = None):

        if base_dir is None:
            # Use default base directory if not provided
            base_dir = _get_default_base_dir()

        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def generate_video_path(self, filename: Optional[str] = None) -> Path:
        """
        Generate path for video file.

        Args:
            filename: Custom filename (without extension)

        Returns:
            Full path for video file
        """
        return self._generate_path(filename, "video", ".mp4")

    def generate_photo_path(self, filename: Optional[str] = None) -> Path:
        """
        Generate path for photo file.

        Args:
            filename: Custom filename (without extension)

        Returns:
            Full path for photo file
        """
        return self._generate_path(filename, "photo", ".jpg")

    def _generate_path(
            self,
            filename: Optional[str],
            file_type: str,
            extension: str
    ) -> Path:
        """
        Generate file path with date-based directory structure.

        Args:
            filename: Custom filename (without extension)
            file_type: Type of file (photo/video) for auto-naming
            extension: File extension (e.g., .mp4, .jpg)

        Returns:
            Complete file path
        """
        now = datetime.datetime.now()

        # Create date-based directory structure: YYYY/MM/DD
        date_folder = (
                self.base_dir
                / now.strftime("%Y")
                / now.strftime("%m")
                / now.strftime("%d")
        )

        # Ensure directory exists
        date_folder.mkdir(parents=True, exist_ok=True)

        if filename:
            # Use provided filename
            if not filename.endswith(extension):
                filename = f"{filename}{extension}"
            return date_folder / filename

        # Auto-generate filename with timestamp
        timestamp = now.strftime('%H%M%S_%f')[:-3]  # HHMMSS_milliseconds
        auto_filename = f"{timestamp}_{file_type}{extension}"

        return date_folder / auto_filename

    def get_today_folder(self) -> Path:
        """Get today's folder path."""
        today = datetime.datetime.now()
        return (
                self.base_dir
                / today.strftime("%Y")
                / today.strftime("%m")
                / today.strftime("%d")
        )

    def cleanup_old_files(self, days_to_keep: int = 30) -> int:
        """
        Clean up files older than specified days.

        Args:
            days_to_keep: Number of days to keep files

        Returns:
            Number of files deleted
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        deleted_count = 0

        try:
            for year_dir in self.base_dir.iterdir():
                if not year_dir.is_dir() or not year_dir.name.isdigit():
                    continue

                for month_dir in year_dir.iterdir():
                    if not month_dir.is_dir() or not month_dir.name.isdigit():
                        continue

                    for day_dir in month_dir.iterdir():
                        if not day_dir.is_dir() or not day_dir.name.isdigit():
                            continue

                        # Check if this date is older than cutoff
                        try:
                            dir_date = datetime.datetime(
                                int(year_dir.name),
                                int(month_dir.name),
                                int(day_dir.name)
                            )

                            if dir_date < cutoff_date:
                                # Delete all files in this day folder
                                for file_path in day_dir.iterdir():
                                    if file_path.is_file():
                                        file_path.unlink()
                                        deleted_count += 1

                                # Remove empty directory
                                if not any(day_dir.iterdir()):
                                    day_dir.rmdir()

                        except (ValueError, OSError):
                            continue

        except Exception as e:
            print(f"Error during cleanup: {e}")

        return deleted_count
