# API Models Package

from .responses import APIResponse, AIProvidersResponse, SystemInfo, HealthStatus, MCPToolsResponse, MCPStatsResponse, \
    MCPTool, TaskResult

from .system_resp import SystemInfoResponse, CPUInfoResponse, DiskInfoResponse, MemoryInfoResponse, NetworkInfoResponse, \
    ProcessInfoResponse, DiskInfoListResponse, NetworkInfoListResponse, ProcessInfoListResponse, SystemHealthResponse

# Type aliases for specific API responses
AIServerListResponse = APIResponse[AIProvidersResponse]
SystemInfoAPIResponse = APIResponse[SystemInfo]
HealthStatusAPIResponse = APIResponse[HealthStatus]
MCPToolsAPIResponse = APIResponse[MCPToolsResponse]
MCPStatsAPIResponse = APIResponse[MCPStatsResponse]
MCPToolDetailAPIResponse = APIResponse[MCPTool]
SystemInfoDetailAPIResponse = APIResponse[SystemInfoResponse]
CPUInfoAPIResponse = APIResponse[CPUInfoResponse]
MemoryInfoAPIResponse = APIResponse[MemoryInfoResponse]
DiskInfoAPIResponse = APIResponse[DiskInfoListResponse]
NetworkInfoAPIResponse = APIResponse[NetworkInfoListResponse]
ProcessInfoAPIResponse = APIResponse[ProcessInfoListResponse]
SystemHealthAPIResponse = APIResponse[SystemHealthResponse]
TaskCreateAPIResponse = APIResponse[TaskResult]

__all__ = [
    "APIResponse",
    "AIServerListResponse",
    "SystemInfoAPIResponse",
    "HealthStatusAPIResponse",
    "MCPToolsAPIResponse",
    "MCPStatsAPIResponse",
    "MCPToolDetailAPIResponse",
    "SystemInfoDetailAPIResponse",
    "CPUInfoAPIResponse",
    "MemoryInfoAPIResponse",
    "DiskInfoAPIResponse",
    "NetworkInfoAPIResponse",
    "ProcessInfoAPIResponse",
    "SystemHealthAPIResponse",
    "TaskCreateAPIResponse"]
