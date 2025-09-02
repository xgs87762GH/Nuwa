"""
Plugin Registration Models
Contains models related to plugin registration and metadata
"""
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from .service import PluginServiceDefinition


@dataclass
class Author:
    name: str
    email: Optional[str] = None


@dataclass
class License:
    text: str


@dataclass
class ProjectUrls:
    repository: Optional[str] = None


@dataclass
class BuildSystem:
    requires: List[str] = field(default_factory=list)
    build_backend: Optional[str] = None


@dataclass
class Project:
    name: str
    version: str
    description: Optional[str] = None
    authors: List[Author] = field(default_factory=list)
    license: Optional[License] = None
    requires_python: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    urls: Optional[ProjectUrls] = None


@dataclass
class PluginMetadata:
    """Plugin metadata information"""
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = ""
    keywords: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    urls: dict = field(default_factory=dict)
    project: Project = field(default_factory=Project),
    build_system: BuildSystem = field(default_factory=BuildSystem)


@dataclass
class PluginRegistration:
    """Complete plugin registration information"""
    path: str  # Plugin directory absolute path
    entry_file: str  # Plugin main entry file (e.g., __init__.py or main.py)
    plugin_services: List[PluginServiceDefinition]  # Plugin service definitions
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Plugin unique identifier (UUID)
    metadata: PluginMetadata = field(default_factory=PluginMetadata)  # Plugin metadata
    load_status: Optional[str] = "pending"  # Load status (pending/loaded/failed)
    error: Optional[str] = None  # Load failure reason
    registered_at: Optional[str] = None  # Registration timestamp
    is_enabled: bool = True  # Whether plugin is enabled

    @property
    def name(self):
        return self.metadata.project.name

    @property
    def description(self):
        return self.metadata.project.description

    @property
    def version(self):
        return self.metadata.project.version

    @property
    def authors(self) -> List[Author]:
        return self.metadata.project.authors

    @property
    def license(self) -> License:
        return self.metadata.project.license

    @property
    def repository(self) -> Optional[str]:
        if self.metadata.project.urls:
            return self.metadata.project.urls.repository
        return None

    @property
    def dependencies(self) -> List[str]:
        return self.metadata.project.dependencies

    @property
    def tags(self):
        return self.metadata.project.keywords
