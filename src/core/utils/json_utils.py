import json


class JsonValidator:
    """
    Simple JSON validation utility class for user Gordon
    Created at: 2025-09-04 09:46:12 UTC
    """

    @staticmethod
    def is_valid_json(content):
        """
        Check if a string is valid JSON format

        Args:
            content: String to validate

        Returns:
            bool: True if valid JSON, False otherwise
        """
        if not content or not isinstance(content, str):
            return False

        try:
            json.loads(content)
            return True
        except (json.JSONDecodeError, ValueError):
            return False
