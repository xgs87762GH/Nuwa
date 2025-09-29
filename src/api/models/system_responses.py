# from typing import List
#
from typing import List, Optional

from pydantic import BaseModel, Field


#
#
# class SystemInfoResponse(BaseModel):
#     """系统信息响应模型"""
#     hostname: str
#     platform: str
#     platform_version: str
#     architecture: str
#     processor: str
#     boot_time: str
#     current_time: str
#
#
# class CPUInfoResponse(BaseModel):
#     """CPU信息响应模型"""
#     physical_cores: int
#     total_cores: int
#     max_frequency: float
#     min_frequency: float
#     current_frequency: float
#     cpu_usage: float
#     cpu_usage_per_core: List[float]
#
#
# class MemoryInfoResponse(BaseModel):
#     """内存信息响应模型"""
#     total: int
#     available: int
#     used: int
#     percentage: float
#     free: int
#
#
# class DiskInfoResponse(BaseModel):
#     """磁盘信息响应模型"""
#     device: str
#     mountpoint: str
#     file_system: str
#     total_size: int
#     used: int
#     free: int
#     percentage: float
#
#
# class NetworkInfoResponse(BaseModel):
#     """网络信息响应模型"""
#     interface: str
#     ip_address: str
#     netmask: str
#     broadcast: str
#     bytes_sent: int
#     bytes_recv: int
#     packets_sent: int
#     packets_recv: int
#
#
# class ProcessInfoResponse(BaseModel):
#     """进程信息响应模型"""
#     pid: int
#     name: str
#     status: str
#     cpu_percent: float
#     memory_percent: float
#     create_time: str


# System Status Models
class SystemInfoResponse(BaseModel):
    """System information response"""
    hostname: str = Field(description="System hostname")
    platform: str = Field(description="Operating system platform")
    platform_version: str = Field(description="OS version")
    architecture: str = Field(description="System architecture")
    processor: str = Field(description="Processor information")
    boot_time: str = Field(description="System boot time")
    current_time: str = Field(description="Current system time")


class CPUInfoResponse(BaseModel):
    """CPU information response"""
    physical_cores: int = Field(description="Number of physical CPU cores")
    total_cores: int = Field(description="Total number of CPU cores")
    max_frequency: float = Field(description="Maximum CPU frequency")
    min_frequency: float = Field(description="Minimum CPU frequency")
    current_frequency: float = Field(description="Current CPU frequency")
    cpu_usage: float = Field(description="Current CPU usage percentage")
    cpu_usage_per_core: List[float] = Field(description="CPU usage per core")


class MemoryInfoResponse(BaseModel):
    """Memory information response"""
    total: int = Field(description="Total memory in bytes")
    available: int = Field(description="Available memory in bytes")
    used: int = Field(description="Used memory in bytes")
    percentage: float = Field(description="Memory usage percentage")
    free: int = Field(description="Free memory in bytes")


class DiskInfoResponse(BaseModel):
    """Disk information response"""
    device: str = Field(description="Device name")
    mountpoint: str = Field(description="Mount point")
    file_system: str = Field(description="File system type")
    total_size: int = Field(description="Total disk size in bytes")
    used: int = Field(description="Used disk space in bytes")
    free: int = Field(description="Free disk space in bytes")
    percentage: float = Field(description="Disk usage percentage")


class DiskInfoListResponse(BaseModel):
    """Disk information list response"""
    disks: List[DiskInfoResponse] = Field(description="List of disk information")
    total_disks: int = Field(description="Total number of disks")


class NetworkInfoResponse(BaseModel):
    """Network information response"""
    interface: str = Field(description="Network interface name")
    ip_address: str = Field(description="IP address")
    netmask: str = Field(description="Network mask")
    broadcast: str = Field(description="Broadcast address")
    bytes_sent: int = Field(description="Total bytes sent")
    bytes_recv: int = Field(description="Total bytes received")
    packets_sent: int = Field(description="Total packets sent")
    packets_recv: int = Field(description="Total packets received")


class NetworkInfoListResponse(BaseModel):
    """Network information list response"""
    interfaces: List[NetworkInfoResponse] = Field(description="List of network interfaces")
    total_interfaces: int = Field(description="Total number of interfaces")


class ProcessInfoResponse(BaseModel):
    """Process information response"""
    pid: int = Field(description="Process ID")
    name: str = Field(description="Process name")
    status: str = Field(description="Process status")
    cpu_percent: float = Field(description="CPU usage percentage")
    memory_percent: float = Field(description="Memory usage percentage")
    create_time: str = Field(description="Process creation time")


class ProcessInfoListResponse(BaseModel):
    """Process information list response"""
    processes: List[ProcessInfoResponse] = Field(description="List of processes")
    total_processes: int = Field(description="Total number of processes")
    limit: int = Field(description="Result limit")


class SystemHealthMetrics(BaseModel):
    """System health metrics"""
    cpu_usage_percent: float = Field(description="CPU usage percentage")
    memory_usage_percent: float = Field(description="Memory usage percentage")
    disk_usage_percent: float = Field(description="Disk usage percentage")
    load_average: Optional[List[float]] = Field(description="System load average")


class SystemHealthResponse(BaseModel):
    """System health check response"""
    status: str = Field(description="Overall system status")
    timestamp: str = Field(description="Health check timestamp")
    metrics: SystemHealthMetrics = Field(description="System metrics")
    alerts: List[str] = Field(description="System alerts")
