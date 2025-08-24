from pathlib import Path


def project_root() -> Path:
    """
    Get the root path of the project.
    """
    return Path(__file__).resolve().parent.parent.parent.parent

