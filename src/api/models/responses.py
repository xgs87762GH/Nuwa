from typing import Dict, Any, List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

# Generic type variable
DataType = TypeVar('DataType')


class APIResponse(BaseModel, Generic[DataType]):
    """Generic API response model"""
    success: bool = Field(description="Whether the request was successful")
    message: str = Field(description="Response message")
    data: Optional[DataType] = Field(default=None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    @classmethod
    def ok(cls, data: DataType = None, message: str = "Success"):
        return cls(success=True, message=message, data=data)

    @classmethod
    def error(cls, message: str = "Error", data: DataType = None):
        return cls(success=False, message=message, data=data)


# AI Provider Models
class AIProviderInfo(BaseModel):
    """AI provider information model"""
    type: str = Field(description="Provider type", example="openai")
    default_model: str = Field(description="Default model name", example="gpt-4")
    models: List[str] = Field(description="Available models", example=["gpt-4", "gpt-3.5-turbo"])
    base_url: str = Field(description="API base URL", example="https://api.openai.com/v1")
    status: str = Field(description="Provider status", example="active")
    initialized_at: str = Field(description="Initialization time", example="2025-09-16 09:54:52")


class AIProvidersResponse(BaseModel):
    """AI providers list response"""
    providers: List[AIProviderInfo] = Field(description="List of AI providers")
    total: int = Field(description="Total number of providers")


# System Info Models
class SystemInfo(BaseModel):
    """System information model"""
    message: str = Field(description="Welcome message")
    version: str = Field(description="Application version")
    documentation: str = Field(description="Documentation URL")


class HealthStatus(BaseModel):
    """Health status model"""
    status: str = Field(description="System status", example="ok")


# MCP Tools Models
class MCPTool(BaseModel):
    """MCP tool model"""
    plugin_name: str = Field(description="Plugin name")
    plugin_id: str = Field(description="Plugin unique identifier")
    description: str = Field(description="Plugin description")
    tags: List[str] = Field(description="Plugin tags")
    version: Optional[str] = Field(description="Plugin version")
    enabled: bool = Field(description="Whether plugin is enabled")


class MCPToolsResponse(BaseModel):
    """MCP tools response"""
    total: int = Field(description="Total number of tools")
    tools: List[MCPTool] = Field(description="List of available tools")


class MCPStatsResponse(BaseModel):
    """MCP statistics response"""
    total: int = Field(description="Total number of plugins")

# Task Models
class TaskResult(BaseModel):
    """Task creation result"""
    task_id: str = Field(description="Created task ID")
    status: str = Field(description="Task status")
    created_at: str = Field(description="Task creation time")
    user_input: str = Field(description="Original user input")
    processed_by: str = Field(description="Processing plugin")

