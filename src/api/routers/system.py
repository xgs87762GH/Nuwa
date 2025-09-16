# System Status API Module
import os
import platform
import socket
from datetime import datetime

import psutil
from fastapi import APIRouter, HTTPException, Request

from src.api.models import APIResponse, SystemInfoResponse, CPUInfoResponse, DiskInfoResponse, MemoryInfoResponse, \
    NetworkInfoResponse, ProcessInfoResponse
from src.core.config import AppConfig
from src.core.config.logger import get_logger

router = APIRouter(prefix="/system")

LOGGER = get_logger(__name__)


@router.get("/info", summary="获取系统基本信息", response_model=APIResponse)
async def get_system_info(req: Request):
    """获取系统基本信息：主机名、平台、架构等"""
    try:
        app_config: AppConfig = req.app.state.app_config
        LOGGER.info(f"获取系统基本信息 - APP: {app_config.name}")

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

        return APIResponse.ok(system_info.dict())
    except Exception as e:
        LOGGER.error(f"获取系统信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")


@router.get("/cpu", summary="获取CPU信息", response_model=APIResponse)
async def get_cpu_info(req: Request):
    """获取CPU信息：核心数、频率、使用率等"""
    try:
        app_config: AppConfig = req.app.state.app_config
        LOGGER.info(f"获取CPU信息 - APP: {app_config.name}")

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

        return APIResponse.ok(cpu_info.dict())
    except Exception as e:
        LOGGER.error(f"获取CPU信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取CPU信息失败: {str(e)}")


@router.get("/memory", summary="获取内存信息", response_model=APIResponse)
async def get_memory_info(req: Request):
    """获取内存信息：总内存、已用内存、可用内存等"""
    try:
        app_config: AppConfig = req.app.state.app_config
        LOGGER.info(f"获取内存信息 - APP: {app_config.name}")

        memory = psutil.virtual_memory()
        memory_info = MemoryInfoResponse(
            total=memory.total,
            available=memory.available,
            used=memory.used,
            percentage=memory.percent,
            free=memory.free
        )

        return APIResponse.ok(memory_info.dict())
    except Exception as e:
        LOGGER.error(f"获取内存信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取内存信息失败: {str(e)}")


@router.get("/disk", summary="获取磁盘信息", response_model=APIResponse)
async def get_disk_info(req: Request):
    """获取磁盘信息：磁盘使用情况、挂载点等"""
    try:
        app_config: AppConfig = req.app.state.app_config
        LOGGER.info(f"获取磁盘信息 - APP: {app_config.name}")

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
                disk_info_list.append(disk_info.dict())
            except PermissionError:
                continue

        # 修改这里：将列表包装在字典中
        return APIResponse.ok({
            "disks": disk_info_list,
            "total_disks": len(disk_info_list)
        })
    except Exception as e:
        LOGGER.error(f"获取磁盘信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取磁盘信息失败: {str(e)}")


@router.get("/network", summary="获取网络信息", response_model=APIResponse)
async def get_network_info(req: Request):
    """获取网络信息：网络接口、IP地址、网络统计等"""
    try:
        app_config: AppConfig = req.app.state.app_config
        LOGGER.info(f"获取网络信息 - APP: {app_config.name}")

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
                    network_info_list.append(network_info.dict())

        # 修改这里：将列表包装在字典中
        return APIResponse.ok({
            "interfaces": network_info_list,
            "total_interfaces": len(network_info_list)
        })
    except Exception as e:
        LOGGER.error(f"获取网络信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取网络信息失败: {str(e)}")


@router.get("/processes", summary="获取进程信息", response_model=APIResponse)
async def get_process_info(req: Request, limit: int = 10):
    """获取进程信息：按CPU使用率排序的前N个进程"""
    try:
        app_config: AppConfig = req.app.state.app_config
        LOGGER.info(f"获取进程信息 - APP: {app_config.name}")

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
                processes.append(process_info.dict())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # 按CPU使用率排序并限制数量
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

        # 修改这里：将列表包装在字典中
        return APIResponse.ok({
            "processes": processes[:limit],
            "total_processes": len(processes),
            "limit": limit
        })
    except Exception as e:
        LOGGER.error(f"获取进程信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取进程信息失败: {str(e)}")


@router.get("/health", summary="系统健康检查", response_model=APIResponse)
async def system_health_check(req: Request):
    """系统健康检查：综合评估系统状态"""
    try:
        app_config: AppConfig = req.app.state.app_config
        LOGGER.info(f"执行系统健康检查 - APP: {app_config.name}")

        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # 磁盘使用率
        try:
            # Windows 系统使用 C:\ 而不是 /
            if platform.system() == "Windows":
                disk_usage = psutil.disk_usage('C:\\')
            else:
                disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
        except:
            disk_percent = 0.0

        # 系统负载（仅Linux/Unix）
        load_avg = None
        if hasattr(os, 'getloadavg'):
            load_avg = os.getloadavg()

        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory_percent,
                "disk_usage_percent": round(disk_percent, 2),
                "load_average": load_avg
            },
            "alerts": []
        }

        # 健康状态判断
        if cpu_percent > 80:
            health_status["alerts"].append("CPU使用率过高")
        if memory_percent > 85:
            health_status["alerts"].append("内存使用率过高")
        if disk_percent > 90:
            health_status["alerts"].append("磁盘使用率过高")

        if health_status["alerts"]:
            health_status["status"] = "warning"

        return APIResponse.ok(health_status)
    except Exception as e:
        LOGGER.error(f"系统健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"系统健康检查失败: {str(e)}")