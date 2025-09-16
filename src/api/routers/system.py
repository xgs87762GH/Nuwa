import os
import platform
import socket
from datetime import datetime

import psutil
from fastapi import APIRouter, Request

from src.api.models import (
    SystemInfoDetailAPIResponse, CPUInfoAPIResponse, MemoryInfoAPIResponse,
    DiskInfoAPIResponse, NetworkInfoAPIResponse, ProcessInfoAPIResponse,
    SystemHealthAPIResponse, SystemInfoResponse, CPUInfoResponse,
    MemoryInfoResponse, DiskInfoResponse, NetworkInfoResponse,
    ProcessInfoResponse, SystemHealthResponse,
    DiskInfoListResponse, NetworkInfoListResponse, ProcessInfoListResponse,
    APIResponse
)
from src.api.models.system_resp import SystemHealthMetrics
from src.core.config import AppConfig
from src.core.config.logger import get_logger

router = APIRouter(prefix="/system", tags=["System Status"])
LOGGER = get_logger(__name__)


@router.get(
    "/info",
    summary="Get system basic information",
    description="Get basic system information including hostname, platform, and architecture",
    response_model=SystemInfoDetailAPIResponse
)
async def get_system_info(req: Request) -> SystemInfoDetailAPIResponse:
    """Get system basic information"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Getting system basic information - APP: {app_config.name}")

    uname = platform.uname()
    boot_time = datetime.fromtimestamp(psutil.boot_time())

    system_info = SystemInfoResponse(
        hostname=uname.node,
        platform=uname.system,
        platform_version=uname.release,
        architecture=uname.machine,
        processor=uname.processor or platform.processor(),
        boot_time=boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return APIResponse.ok(data=system_info)


@router.get(
    "/cpu",
    summary="Get CPU information",
    description="Get CPU information including cores, frequency, and usage",
    response_model=CPUInfoAPIResponse
)
async def get_cpu_info(req: Request) -> CPUInfoAPIResponse:
    """Get CPU information"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Getting CPU information - APP: {app_config.name}")

    cpu_freq = psutil.cpu_freq()
    cpu_info = CPUInfoResponse(
        physical_cores=psutil.cpu_count(logical=False),
        total_cores=psutil.cpu_count(logical=True),
        max_frequency=cpu_freq.max if cpu_freq else 0.0,
        min_frequency=cpu_freq.min if cpu_freq else 0.0,
        current_frequency=cpu_freq.current if cpu_freq else 0.0,
        cpu_usage=psutil.cpu_percent(interval=1),
        cpu_usage_per_core=psutil.cpu_percent(interval=1, percpu=True)
    )

    return APIResponse.ok(data=cpu_info)


@router.get(
    "/memory",
    summary="Get memory information",
    description="Get memory information including total, used, and available memory",
    response_model=MemoryInfoAPIResponse
)
async def get_memory_info(req: Request) -> MemoryInfoAPIResponse:
    """Get memory information"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Getting memory information - APP: {app_config.name}")

    memory = psutil.virtual_memory()
    memory_info = MemoryInfoResponse(
        total=memory.total,
        available=memory.available,
        used=memory.used,
        percentage=memory.percent,
        free=memory.free
    )

    return APIResponse.ok(data=memory_info)


@router.get(
    "/disk",
    summary="Get disk information",
    description="Get disk information including disk usage and mount points",
    response_model=DiskInfoAPIResponse
)
async def get_disk_info(req: Request) -> DiskInfoAPIResponse:
    """Get disk information"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Getting disk information - APP: {app_config.name}")

    disk_info_list = []
    partitions = psutil.disk_partitions()

    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            disk_info = DiskInfoResponse(
                device=partition.device,
                mountpoint=partition.mountpoint,
                file_system=partition.fstype,
                total_size=partition_usage.total,
                used=partition_usage.used,
                free=partition_usage.free,
                percentage=round((partition_usage.used / partition_usage.total) * 100, 2)
            )
            disk_info_list.append(disk_info)
        except PermissionError:
            continue

    response_data = DiskInfoListResponse(
        disks=disk_info_list,
        total_disks=len(disk_info_list)
    )

    return APIResponse.ok(data=response_data)


@router.get(
    "/network",
    summary="Get network information",
    description="Get network information including interfaces, IP addresses, and network statistics",
    response_model=NetworkInfoAPIResponse
)
async def get_network_info(req: Request) -> NetworkInfoAPIResponse:
    """Get network information"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Getting network information - APP: {app_config.name}")

    network_info_list = []
    network_io = psutil.net_io_counters(pernic=True)
    network_addrs = psutil.net_if_addrs()

    for interface_name, interface_addrs in network_addrs.items():
        for addr in interface_addrs:
            if addr.family == socket.AF_INET:  # IPv4
                io_stats = network_io.get(interface_name)
                network_info = NetworkInfoResponse(
                    interface=interface_name,
                    ip_address=addr.address,
                    netmask=addr.netmask,
                    broadcast=addr.broadcast or "",
                    bytes_sent=io_stats.bytes_sent if io_stats else 0,
                    bytes_recv=io_stats.bytes_recv if io_stats else 0,
                    packets_sent=io_stats.packets_sent if io_stats else 0,
                    packets_recv=io_stats.packets_recv if io_stats else 0
                )
                network_info_list.append(network_info)

    response_data = NetworkInfoListResponse(
        interfaces=network_info_list,
        total_interfaces=len(network_info_list)
    )

    return APIResponse.ok(data=response_data)


@router.get(
    "/processes",
    summary="Get process information",
    description="Get process information sorted by CPU usage",
    response_model=ProcessInfoAPIResponse
)
async def get_process_info(req: Request, limit: int = 10) -> ProcessInfoAPIResponse:
    """Get process information"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Getting process information - APP: {app_config.name}")

    processes = []
    for process in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            process_info = ProcessInfoResponse(
                pid=process.info['pid'],
                name=process.info['name'],
                status=process.info['status'],
                cpu_percent=process.info['cpu_percent'] or 0.0,
                memory_percent=process.info['memory_percent'] or 0.0,
                create_time=datetime.fromtimestamp(process.info['create_time']).strftime("%Y-%m-%d %H:%M:%S")
            )
            processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sort by CPU usage and limit results
    processes.sort(key=lambda x: x.cpu_percent, reverse=True)

    response_data = ProcessInfoListResponse(
        processes=processes[:limit],
        total_processes=len(processes),
        limit=limit
    )

    return APIResponse.ok(data=response_data)


@router.get(
    "/health",
    summary="System health check",
    description="Comprehensive system health assessment",
    response_model=SystemHealthAPIResponse
)
async def system_health_check(req: Request) -> SystemHealthAPIResponse:
    """System health check"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Performing system health check - APP: {app_config.name}")

    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)

    # Memory usage
    memory = psutil.virtual_memory()
    memory_percent = memory.percent

    # Disk usage
    try:
        if platform.system() == "Windows":
            disk_usage = psutil.disk_usage('C:\\')
        else:
            disk_usage = psutil.disk_usage('/')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
    except:
        disk_percent = 0.0

    # System load (Linux/Unix only)
    load_avg = None
    if hasattr(os, 'getloadavg'):
        load_avg = list(os.getloadavg())

    metrics = SystemHealthMetrics(
        cpu_usage_percent=cpu_percent,
        memory_usage_percent=memory_percent,
        disk_usage_percent=round(disk_percent, 2),
        load_average=load_avg
    )

    alerts = []
    status = "healthy"

    # Health assessment
    if cpu_percent > 80:
        alerts.append("CPU usage is too high")
    if memory_percent > 85:
        alerts.append("Memory usage is too high")
    if disk_percent > 90:
        alerts.append("Disk usage is too high")

    if alerts:
        status = "warning"

    health_status = SystemHealthResponse(
        status=status,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        metrics=metrics,
        alerts=alerts
    )

    return APIResponse.ok(data=health_status)
