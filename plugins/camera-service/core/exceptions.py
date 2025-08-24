"""Core exceptions for camera service."""


class CameraServiceError(Exception):
    """Base exception for camera service."""
    pass


class ValidationError(CameraServiceError):
    """Raised when parameter validation fails."""
    pass
