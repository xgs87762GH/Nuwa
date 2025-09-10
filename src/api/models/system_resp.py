from typing import List

from pydantic import BaseModel


class SystemInfoResponse(BaseModel):
    """系统信息响应模型"""
    hostname: str
    platform: str
    platform_version: str
    architecture: str
    processor: str
    boot_time: str
    current_time: str


class CPUInfoResponse(BaseModel):
    """CPU信息响应模型"""
    physical_cores: int
    total_cores: int
    max_frequency: float
    min_frequency: float
    current_frequency: float
    cpu_usage: float
    cpu_usage_per_core: List[float]


class MemoryInfoResponse(BaseModel):
    """内存信息响应模型"""
    total: int
    available: int
    used: int
    percentage: float
    free: int


class DiskInfoResponse(BaseModel):
    """磁盘信息响应模型"""
    device: str
    mountpoint: str
    file_system: str
    total_size: int
    used: int
    free: int
    percentage: float


class NetworkInfoResponse(BaseModel):
    """网络信息响应模型"""
    interface: str
    ip_address: str
    netmask: str
    broadcast: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


class ProcessInfoResponse(BaseModel):
    """进程信息响应模型"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    create_time: str
