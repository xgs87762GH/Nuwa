import os
import platform
import socket
import asyncio
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, List
from functools import wraps

import psutil
from fastapi import APIRouter, Request, BackgroundTasks

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

# 全局线程池执行器
executor = ThreadPoolExecutor(max_workers=6, thread_name_prefix="system_monitor")

# 缓存配置
CACHE_TTL = {
    'system_info': 30,  # 系统基础信息缓存30秒
    'cpu': 2,  # CPU信息缓存2秒
    'memory': 1,  # 内存信息缓存1秒
    'disk': 10,  # 磁盘信息缓存10秒
    'network': 5,  # 网络信息缓存5秒
    'processes': 3,  # 进程信息缓存3秒
}

# 全局缓存
_cache: Dict[str, Dict[str, Any]] = {}


def cache_result(cache_key: str, ttl: int):
    """缓存装饰器，支持异步函数"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()

            # 检查缓存
            if cache_key in _cache:
                cached_data = _cache[cache_key]
                if now - cached_data['timestamp'] < ttl:
                    return cached_data['data']

            # 执行函数获取新数据
            result = await func(*args, **kwargs)

            # 更新缓存
            _cache[cache_key] = {
                'data': result,
                'timestamp': now
            }

            return result

        return wrapper

    return decorator


async def run_in_executor(func, *args):
    """在线程池中执行同步函数"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


def get_cpu_data_sync():
    """同步获取CPU数据"""
    # 使用非阻塞方式获取CPU使用率
    cpu_percent = psutil.cpu_percent(interval=0.1)  # 减少到0.1秒
    cpu_freq = psutil.cpu_freq()
    cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)

    return {
        'physical_cores': psutil.cpu_count(logical=False),
        'total_cores': psutil.cpu_count(logical=True),
        'max_frequency': cpu_freq.max if cpu_freq else 0.0,
        'min_frequency': cpu_freq.min if cpu_freq else 0.0,
        'current_frequency': cpu_freq.current if cpu_freq else 0.0,
        'cpu_usage': cpu_percent,
        'cpu_usage_per_core': cpu_per_core
    }


def get_memory_data_sync():
    """同步获取内存数据"""
    memory = psutil.virtual_memory()
    return {
        'total': memory.total,
        'available': memory.available,
        'used': memory.used,
        'percentage': memory.percent,
        'free': memory.free
    }


def get_disk_data_sync():
    """同步获取磁盘数据"""
    disk_info_list = []
    partitions = psutil.disk_partitions()

    for partition in partitions:
        try:
            # 跳过某些特殊文件系统
            if partition.fstype in ['tmpfs', 'devtmpfs', 'squashfs']:
                continue

            partition_usage = psutil.disk_usage(partition.mountpoint)
            disk_info = {
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'file_system': partition.fstype,
                'total_size': partition_usage.total,
                'used': partition_usage.used,
                'free': partition_usage.free,
                'percentage': round((partition_usage.used / partition_usage.total) * 100, 2)
            }
            disk_info_list.append(disk_info)
        except (PermissionError, OSError):
            continue

    return disk_info_list


def get_network_data_sync():
    """同步获取网络数据 - 优化版"""
    network_info_list = []

    # 并行获取网络IO和地址信息
    network_io = psutil.net_io_counters(pernic=True)
    network_addrs = psutil.net_if_addrs()

    # 只处理有流量的活跃接口
    active_interfaces = {
        name: stats for name, stats in network_io.items()
        if stats.bytes_sent > 0 or stats.bytes_recv > 0
    }

    for interface_name, io_stats in active_interfaces.items():
        interface_addrs = network_addrs.get(interface_name, [])

        # 只获取第一个IPv4地址
        for addr in interface_addrs:
            if addr.family == socket.AF_INET:
                network_info = {
                    'interface': interface_name,
                    'ip_address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast or "",
                    'bytes_sent': io_stats.bytes_sent,
                    'bytes_recv': io_stats.bytes_recv,
                    'packets_sent': io_stats.packets_sent,
                    'packets_recv': io_stats.packets_recv
                }
                network_info_list.append(network_info)
                break  # 每个接口只取一个IPv4

    return network_info_list


def get_processes_data_sync(limit: int = 10):
    """同步获取进程数据 - 优化版"""
    processes = []
    process_count = 0

    # 使用更高效的进程遍历
    for process in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            info = process.info

            # 预筛选：跳过CPU使用率为0的进程
            cpu_percent = info.get('cpu_percent', 0) or 0.0
            if cpu_percent < 0.1:
                continue

            process_info = {
                'pid': info['pid'],
                'name': info['name'],
                'status': info['status'],
                'cpu_percent': cpu_percent,
                'memory_percent': info.get('memory_percent', 0) or 0.0,
                'create_time': datetime.fromtimestamp(info['create_time']).strftime("%Y-%m-%d %H:%M:%S")
            }
            processes.append(process_info)

            # 早期截断：收集到足够多的活跃进程就停止
            if len(processes) >= limit * 3:
                break

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

        process_count += 1
        # 防止遍历过多进程
        if process_count > 500:
            break

    # 按CPU使用率排序并限制数量
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes[:limit]


@cache_result('system_info', CACHE_TTL['system_info'])
async def get_cached_system_info():
    """获取缓存的系统基础信息"""
    return await run_in_executor(lambda: {
        'uname': platform.uname(),
        'boot_time': datetime.fromtimestamp(psutil.boot_time()),
        'current_time': datetime.now()
    })


@cache_result('cpu', CACHE_TTL['cpu'])
async def get_cached_cpu_info():
    """获取缓存的CPU信息"""
    return await run_in_executor(get_cpu_data_sync)


@cache_result('memory', CACHE_TTL['memory'])
async def get_cached_memory_info():
    """获取缓存的内存信息"""
    return await run_in_executor(get_memory_data_sync)


@cache_result('disk', CACHE_TTL['disk'])
async def get_cached_disk_info():
    """获取缓存的磁盘信息"""
    return await run_in_executor(get_disk_data_sync)


@cache_result('network', CACHE_TTL['network'])
async def get_cached_network_info():
    """获取缓存的网络信息"""
    return await run_in_executor(get_network_data_sync)


def get_cached_processes_info(limit: int):
    """获取缓存的进程信息（动态缓存键）"""
    cache_key = f'processes_{limit}'

    async def _get_processes():
        return await run_in_executor(get_processes_data_sync, limit)

    return cache_result(cache_key, CACHE_TTL['processes'])(_get_processes)()


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

    data = await get_cached_system_info()
    uname = data['uname']
    boot_time = data['boot_time']
    current_time = data['current_time']

    system_info = SystemInfoResponse(
        hostname=uname.node,
        platform=uname.system,
        platform_version=uname.release,
        architecture=uname.machine,
        processor=uname.processor or platform.processor(),
        boot_time=boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        current_time=current_time.strftime("%Y-%m-%d %H:%M:%S")
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

    data = await get_cached_cpu_info()

    cpu_info = CPUInfoResponse(
        physical_cores=data['physical_cores'],
        total_cores=data['total_cores'],
        max_frequency=data['max_frequency'],
        min_frequency=data['min_frequency'],
        current_frequency=data['current_frequency'],
        cpu_usage=data['cpu_usage'],
        cpu_usage_per_core=data['cpu_usage_per_core']
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

    data = await get_cached_memory_info()

    memory_info = MemoryInfoResponse(
        total=data['total'],
        available=data['available'],
        used=data['used'],
        percentage=data['percentage'],
        free=data['free']
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

    disk_info_list = await get_cached_disk_info()

    disk_responses = [
        DiskInfoResponse(
            device=disk['device'],
            mountpoint=disk['mountpoint'],
            file_system=disk['file_system'],
            total_size=disk['total_size'],
            used=disk['used'],
            free=disk['free'],
            percentage=disk['percentage']
        ) for disk in disk_info_list
    ]

    response_data = DiskInfoListResponse(
        disks=disk_responses,
        total_disks=len(disk_responses)
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

    network_info_list = await get_cached_network_info()

    network_responses = [
        NetworkInfoResponse(
            interface=net['interface'],
            ip_address=net['ip_address'],
            netmask=net['netmask'],
            broadcast=net['broadcast'],
            bytes_sent=net['bytes_sent'],
            bytes_recv=net['bytes_recv'],
            packets_sent=net['packets_sent'],
            packets_recv=net['packets_recv']
        ) for net in network_info_list
    ]

    response_data = NetworkInfoListResponse(
        interfaces=network_responses,
        total_interfaces=len(network_responses)
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

    processes_data = await get_cached_processes_info(limit)

    process_responses = [
        ProcessInfoResponse(
            pid=proc['pid'],
            name=proc['name'],
            status=proc['status'],
            cpu_percent=proc['cpu_percent'],
            memory_percent=proc['memory_percent'],
            create_time=proc['create_time']
        ) for proc in processes_data
    ]

    response_data = ProcessInfoListResponse(
        processes=process_responses,
        total_processes=len(process_responses),
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

    # 并行获取关键指标
    tasks = [
        get_cached_cpu_info(),
        get_cached_memory_info(),
    ]

    cpu_data, memory_data = await asyncio.gather(*tasks)

    # 获取磁盘使用率
    try:
        if platform.system() == "Windows":
            disk_usage = await run_in_executor(psutil.disk_usage, 'C:\\')
        else:
            disk_usage = await run_in_executor(psutil.disk_usage, '/')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
    except:
        disk_percent = 0.0

    # 系统负载 (Linux/Unix only)
    load_avg = None
    if hasattr(os, 'getloadavg'):
        try:
            load_avg = await run_in_executor(os.getloadavg)
            load_avg = list(load_avg)
        except:
            load_avg = None

    metrics = SystemHealthMetrics(
        cpu_usage_percent=cpu_data['cpu_usage'],
        memory_usage_percent=memory_data['percentage'],
        disk_usage_percent=round(disk_percent, 2),
        load_average=load_avg
    )

    alerts = []
    status = "healthy"

    # 健康评估
    if cpu_data['cpu_usage'] > 80:
        alerts.append("CPU usage is too high")
    if memory_data['percentage'] > 85:
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


# 新增：快速健康检查端点
@router.get(
    "/health/quick",
    summary="Quick health check",
    description="Fast health check with minimal system calls"
)
async def quick_health_check(req: Request):
    """Quick health check - 实时数据，无缓存"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Performing quick health check - APP: {app_config.name}")

    # 获取实时数据（不使用缓存）
    cpu_percent = await run_in_executor(psutil.cpu_percent, 0)  # 非阻塞
    memory = await run_in_executor(psutil.virtual_memory)

    status = "healthy"
    alerts = []

    if cpu_percent > 80:
        status = "warning"
        alerts.append("High CPU usage")
    if memory.percent > 85:
        status = "warning"
        alerts.append("High memory usage")

    return APIResponse.ok(data={
        "status": status,
        "cpu_usage": round(cpu_percent, 2),
        "memory_usage": round(memory.percent, 2),
        "alerts": alerts,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# 新增：批量获取系统概览
@router.get(
    "/overview",
    summary="System overview",
    description="Get comprehensive system overview with optimized performance"
)
async def get_system_overview(req: Request):
    """获取系统概览 - 并行获取所有数据"""
    app_config: AppConfig = req.app.state.app_config
    LOGGER.info(f"Getting system overview - APP: {app_config.name}")

    # 并行获取所有缓存数据
    tasks = [
        get_cached_cpu_info(),
        get_cached_memory_info(),
        get_cached_disk_info(),
        get_cached_network_info(),
    ]

    cpu_data, memory_data, disk_data, network_data = await asyncio.gather(*tasks)

    overview = {
        "cpu": {
            "usage": cpu_data['cpu_usage'],
            "cores": cpu_data['total_cores']
        },
        "memory": {
            "usage_percent": memory_data['percentage'],
            "total_gb": round(memory_data['total'] / (1024 ** 3), 2),
            "available_gb": round(memory_data['available'] / (1024 ** 3), 2)
        },
        "disk": {
            "partitions": len(disk_data),
            "total_usage_percent": round(
                sum(disk['percentage'] for disk in disk_data) / len(disk_data), 2
            ) if disk_data else 0
        },
        "network": {
            "active_interfaces": len(network_data),
            "total_bytes_sent": sum(net['bytes_sent'] for net in network_data),
            "total_bytes_recv": sum(net['bytes_recv'] for net in network_data)
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return APIResponse.ok(data=overview)


# 清理缓存的后台任务
async def cleanup_cache():
    """清理过期缓存"""
    current_time = time.time()
    expired_keys = []

    for key, data in _cache.items():
        # 如果缓存项超过最大TTL的2倍，则清理
        max_ttl = max(CACHE_TTL.values())
        if current_time - data['timestamp'] > max_ttl * 2:
            expired_keys.append(key)

    for key in expired_keys:
        _cache.pop(key, None)

    LOGGER.info(f"Cleaned up {len(expired_keys)} expired cache entries")


@router.get("/cache/status")
async def get_cache_status():
    """获取缓存状态"""
    current_time = time.time()
    cache_info = {}

    for key, data in _cache.items():
        age = current_time - data['timestamp']
        cache_info[key] = {
            "age_seconds": round(age, 2),
            "data_size": len(str(data['data'])),
            "expired": age > CACHE_TTL.get(key.split('_')[0], 30)
        }

    return APIResponse.ok(data={
        "total_entries": len(_cache),
        "cache_details": cache_info,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# 应用启动时初始化
@router.on_event("startup")
async def startup_system_monitor():
    """启动时预热缓存"""
    LOGGER.info("Initializing system monitor with cache prewarming...")

    # 预热关键缓存
    try:
        await asyncio.gather(
            get_cached_cpu_info(),
            get_cached_memory_info(),
            return_exceptions=True
        )
        LOGGER.info("Cache prewarming completed successfully")
    except Exception as e:
        LOGGER.warning(f"Cache prewarming failed: {e}")


@router.on_event("shutdown")
async def shutdown_system_monitor():
    """关闭时清理资源"""
    LOGGER.info("Shutting down system monitor...")
    executor.shutdown(wait=True)
    _cache.clear()
    LOGGER.info("System monitor shutdown completed")
