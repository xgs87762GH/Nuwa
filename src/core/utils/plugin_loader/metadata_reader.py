"""
Plugin Metadata Reader
Handles reading and parsing of plugin metadata from configuration files
"""
import datetime
import tomllib
from pathlib import Path
from typing import Dict, Any, List

from src.core.config import get_logger

logger = get_logger("metadata_reader")


class ProjectMetadataReader:
    """
    Metadata Extractor
    Reads pyproject.toml from specified plugin directory and caches the result
    """

    __slots__ = ("_metadata",)

    def __init__(self, plugin_path: str | Path) -> None:
        self._metadata: Dict[str, Any] = self._load(plugin_path)

    # ------------- Public Interface -------------
    @property
    def metadata(self) -> Dict[str, Any]:
        """Read-only access to metadata"""
        return self._metadata

    @property
    def project(self) -> Dict[str, Any]:
        return self._metadata.get("project", {})

    @property
    def dependencies(self) -> List[str]:
        return self.project.get("dependencies", [])

    @property
    def urls(self) -> Dict[str, str]:
        return self.project.get("urls", {})

    @property
    def build_system(self) -> Dict[str, Any]:
        return self._metadata.get("build_system", {})

    # ------------- Internal Implementation -------------
    @staticmethod
    def _load(plugin_path: str | Path) -> Dict[str, Any]:
        path = Path(plugin_path, "pyproject.toml")
        if not path.exists():
            logger.warning(f"pyproject.toml not found at path: {path}")
            return {}

        try:
            with path.open("rb") as fp:
                data = tomllib.load(fp)

            logger.debug(f"Successfully loaded metadata from: {path}")
            return {
                "build_system": data.get("build-system", {}),
                "project": data.get("project", {}),
                "loaded_at": datetime.datetime.now(tz=datetime.timezone.utc)
                .replace(microsecond=0)
                .isoformat(),
                "loaded_by": data.get("loaded_by", "unknown"),
            }
        except Exception as exc:
            logger.error(f"Error loading pyproject.toml from {path}: {str(exc)}")
            return {"error": str(exc)}
