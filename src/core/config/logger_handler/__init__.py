import logging
import sys


class ColoredFormatter(logging.Formatter):
    """Simple colored formatter"""

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Purple
        'RESET': '\033[0m'  # Reset
    }

    def format(self, record):
        if sys.stderr.isatty():  # Show colors only in terminal
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)




__all__ = [
    "ColoredFormatter"
]

