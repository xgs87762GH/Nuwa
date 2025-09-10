from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api.routers.system import router
from src.core.config import AppConfig


class TestSystemAPI:
    """系统 API 单元测试类"""

    @pytest.fixture
    def mock_app_config(self):
        """模拟应用配置"""
        config = Mock(spec=AppConfig)
        config.name = "Test Nuwa API"
        config.version = "1.0.0"
        return config

    @pytest.fixture
    def mock_request(self, mock_app_config):
        """模拟请求对象"""
        request = Mock()
        request.app.state.app_config = mock_app_config
        return request

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)

        # 模拟应用状态
        app.state.app_config = Mock()
        app.state.app_config.name = "Test Nuwa API"

        return TestClient(app)

    class TestGetSystemInfo:
        """测试获取系统基本信息接口"""

        @patch('src.api.routers.system.platform.uname')
        @patch('src.api.routers.system.psutil.boot_time')
        @patch('src.api.routers.system.datetime')
        async def test_get_system_info_success(self, mock_datetime, mock_boot_time, mock_uname, mock_request):
            """测试成功获取系统信息"""
            from src.api.routers.system import get_system_info

            # 设置模拟数据
            mock_uname_result = Mock()
            mock_uname_result.node = "test-hostname"
            mock_uname_result.system = "Linux"
            mock_uname_result.release = "5.15.0"
            mock_uname_result.machine = "x86_64"
            mock_uname_result.processor = "Intel Core i7"
            mock_uname.return_value = mock_uname_result

            mock_boot_time.return_value = 1672531200.0  # 2023-01-01 00:00:00

            mock_boot_datetime = Mock()
            mock_boot_datetime.strftime.return_value = "2023-01-01 00:00:00"

            mock_current_datetime = Mock()
            mock_current_datetime.strftime.return_value = "2025-09-10 09:38:41"

            mock_datetime.fromtimestamp.return_value = mock_boot_datetime
            mock_datetime.now.return_value = mock_current_datetime

            # 执行测试
            result = await get_system_info(mock_request)

            # 验证结果
            assert result.success is True
            assert result.message == "Success"
            assert result.data is not None
            assert result.data["hostname"] == "test-hostname"
            assert result.data["platform"] == "Linux"
            assert result.data["platform_version"] == "5.15.0"
            assert result.data["architecture"] == "x86_64"
            assert result.data["processor"] == "Intel Core i7"
            assert result.data["boot_time"] == "2023-01-01 00:00:00"
            assert result.data["current_time"] == "2025-09-10 09:38:41"

        @patch('src.api.routers.system.platform.uname')
        async def test_get_system_info_error(self, mock_uname, mock_request):
            """测试获取系统信息时发生异常"""
            from src.api.routers.system import get_system_info

            # 设置异常
            mock_uname.side_effect = Exception("System error")

            # 执行测试并验证异常
            with pytest.raises(HTTPException) as exc_info:
                await get_system_info(mock_request)

            assert exc_info.value.status_code == 500
            assert "获取系统信息失败: System error" in str(exc_info.value.detail)

    class TestGetCPUInfo:
        """测试获取 CPU 信息接口"""

        @patch('src.api.routers.system.psutil.cpu_count')
        @patch('src.api.routers.system.psutil.cpu_freq')
        @patch('src.api.routers.system.psutil.cpu_percent')
        async def test_get_cpu_info_success(self, mock_cpu_percent, mock_cpu_freq, mock_cpu_count, mock_request):
            """测试成功获取 CPU 信息"""
            from src.api.routers.system import get_cpu_info

            # 设置模拟数据
            mock_cpu_count.side_effect = [4, 8]  # physical_cores, total_cores

            mock_freq = Mock()
            mock_freq.max = 3600.0
            mock_freq.min = 800.0
            mock_freq.current = 2400.0
            mock_cpu_freq.return_value = mock_freq

            mock_cpu_percent.side_effect = [25.5, [10.0, 20.0, 30.0, 40.0, 15.0, 25.0, 35.0, 45.0]]

            # 执行测试
            result = await get_cpu_info(mock_request)

            # 验证结果
            assert result.success is True
            assert result.data["physical_cores"] == 4
            assert result.data["total_cores"] == 8
            assert result.data["max_frequency"] == 3600.0
            assert result.data["min_frequency"] == 800.0
            assert result.data["current_frequency"] == 2400.0
            assert result.data["cpu_usage"] == 25.5
            assert len(result.data["cpu_usage_per_core"]) == 8

        @patch('src.api.routers.system.psutil.cpu_count')
        @patch('src.api.routers.system.psutil.cpu_freq')
        @patch('src.api.routers.system.psutil.cpu_percent')
        async def test_get_cpu_info_no_freq_data(self, mock_cpu_percent, mock_cpu_freq, mock_cpu_count, mock_request):
            """测试 CPU 频率信息不可用的情况"""
            from src.api.routers.system import get_cpu_info

            # 设置模拟数据
            mock_cpu_count.side_effect = [2, 4]
            mock_cpu_freq.return_value = None  # 模拟频率信息不可用
            mock_cpu_percent.side_effect = [15.0, [10.0, 20.0, 5.0, 25.0]]

            # 执行测试
            result = await get_cpu_info(mock_request)

            # 验证结果
            assert result.success is True
            assert result.data["max_frequency"] == 0.0
            assert result.data["min_frequency"] == 0.0
            assert result.data["current_frequency"] == 0.0

        @patch('src.api.routers.system.psutil.cpu_count')
        async def test_get_cpu_info_error(self, mock_cpu_count, mock_request):
            """测试获取 CPU 信息时发生异常"""
            from src.api.routers.system import get_cpu_info

            # 设置异常
            mock_cpu_count.side_effect = Exception("CPU error")

            # 执行测试并验证异常
            with pytest.raises(HTTPException) as exc_info:
                await get_cpu_info(mock_request)

            assert exc_info.value.status_code == 500
            assert "获取CPU信息失败: CPU error" in str(exc_info.value.detail)

    class TestGetMemoryInfo:
        """测试获取内存信息接口"""

        @patch('src.api.routers.system.psutil.virtual_memory')
        async def test_get_memory_info_success(self, mock_virtual_memory, mock_request):
            """测试成功获取内存信息"""
            from src.api.routers.system import get_memory_info

            # 设置模拟数据
            mock_memory = Mock()
            mock_memory.total = 16 * 1024 * 1024 * 1024  # 16GB
            mock_memory.available = 8 * 1024 * 1024 * 1024  # 8GB
            mock_memory.used = 8 * 1024 * 1024 * 1024  # 8GB
            mock_memory.percent = 50.0
            mock_memory.free = 8 * 1024 * 1024 * 1024  # 8GB
            mock_virtual_memory.return_value = mock_memory

            # 执行测试
            result = await get_memory_info(mock_request)

            # 验证结果
            assert result.success is True
            assert result.data["total"] == 16 * 1024 * 1024 * 1024
            assert result.data["available"] == 8 * 1024 * 1024 * 1024
            assert result.data["used"] == 8 * 1024 * 1024 * 1024
            assert result.data["percentage"] == 50.0
            assert result.data["free"] == 8 * 1024 * 1024 * 1024

        @patch('src.api.routers.system.psutil.virtual_memory')
        async def test_get_memory_info_error(self, mock_virtual_memory, mock_request):
            """测试获取内存信息时发生异常"""
            from src.api.routers.system import get_memory_info

            # 设置异常
            mock_virtual_memory.side_effect = Exception("Memory error")

            # 执行测试并验证异常
            with pytest.raises(HTTPException) as exc_info:
                await get_memory_info(mock_request)

            assert exc_info.value.status_code == 500
            assert "获取内存信息失败: Memory error" in str(exc_info.value.detail)

    class TestGetDiskInfo:
        """测试获取磁盘信息接口"""

        @patch('src.api.routers.system.psutil.disk_partitions')
        @patch('src.api.routers.system.psutil.disk_usage')
        async def test_get_disk_info_success(self, mock_disk_usage, mock_disk_partitions, mock_request):
            """测试成功获取磁盘信息"""
            from src.api.routers.system import get_disk_info

            # 设置模拟分区数据
            mock_partition1 = Mock()
            mock_partition1.device = "/dev/sda1"
            mock_partition1.mountpoint = "/"
            mock_partition1.fstype = "ext4"

            mock_partition2 = Mock()
            mock_partition2.device = "/dev/sda2"
            mock_partition2.mountpoint = "/home"
            mock_partition2.fstype = "ext4"

            mock_disk_partitions.return_value = [mock_partition1, mock_partition2]

            # 设置模拟使用情况数据
            mock_usage1 = Mock()
            mock_usage1.total = 100 * 1024 * 1024 * 1024  # 100GB
            mock_usage1.used = 50 * 1024 * 1024 * 1024  # 50GB
            mock_usage1.free = 50 * 1024 * 1024 * 1024  # 50GB

            mock_usage2 = Mock()
            mock_usage2.total = 200 * 1024 * 1024 * 1024  # 200GB
            mock_usage2.used = 80 * 1024 * 1024 * 1024  # 80GB
            mock_usage2.free = 120 * 1024 * 1024 * 1024  # 120GB

            mock_disk_usage.side_effect = [mock_usage1, mock_usage2]

            # 执行测试
            result = await get_disk_info(mock_request)

            # 验证结果
            assert result.success is True
            assert len(result.data) == 2

            disk1 = result.data[0]
            assert disk1["device"] == "/dev/sda1"
            assert disk1["mountpoint"] == "/"
            assert disk1["file_system"] == "ext4"
            assert disk1["percentage"] == 50.0

            disk2 = result.data[1]
            assert disk2["device"] == "/dev/sda2"
            assert disk2["mountpoint"] == "/home"
            assert disk2["percentage"] == 40.0

        @patch('src.api.routers.system.psutil.disk_partitions')
        @patch('src.api.routers.system.psutil.disk_usage')
        async def test_get_disk_info_permission_error(self, mock_disk_usage, mock_disk_partitions, mock_request):
            """测试磁盘访问权限异常的情况"""
            from src.api.routers.system import get_disk_info

            # 设置模拟分区数据
            mock_partition = Mock()
            mock_partition.device = "/dev/restricted"
            mock_partition.mountpoint = "/restricted"
            mock_partition.fstype = "ntfs"

            mock_disk_partitions.return_value = [mock_partition]

            # 设置权限异常
            mock_disk_usage.side_effect = PermissionError("Access denied")

            # 执行测试
            result = await get_disk_info(mock_request)

            # 验证结果 - 应该跳过没有权限的分区
            assert result.success is True
            assert result.data == []

        @patch('src.api.routers.system.psutil.disk_partitions')
        async def test_get_disk_info_error(self, mock_disk_partitions, mock_request):
            """测试获取磁盘信息时发生异常"""
            from src.api.routers.system import get_disk_info

            # 设置异常
            mock_disk_partitions.side_effect = Exception("Disk error")

            # 执行测试并验证异常
            with pytest.raises(HTTPException) as exc_info:
                await get_disk_info(mock_request)

            assert exc_info.value.status_code == 500
            assert "获取磁盘信息失败: Disk error" in str(exc_info.value.detail)

    class TestGetNetworkInfo:
        """测试获取网络信息接口"""

        @patch('src.api.routers.system.psutil.net_io_counters')
        @patch('src.api.routers.system.psutil.net_if_addrs')
        @patch('src.api.routers.system.socket')
        async def test_get_network_info_success(self, mock_socket, mock_net_if_addrs, mock_net_io_counters,
                                                mock_request):
            """测试成功获取网络信息"""
            from src.api.routers.system import get_network_info

            # 设置模拟网络地址数据
            mock_addr = Mock()
            mock_addr.family = mock_socket.AF_INET
            mock_addr.address = "192.168.1.100"
            mock_addr.netmask = "255.255.255.0"
            mock_addr.broadcast = "192.168.1.255"

            mock_net_if_addrs.return_value = {
                "eth0": [mock_addr]
            }

            # 设置模拟网络 IO 统计数据
            mock_io_stats = Mock()
            mock_io_stats.bytes_sent = 1024 * 1024  # 1MB
            mock_io_stats.bytes_recv = 2 * 1024 * 1024  # 2MB
            mock_io_stats.packets_sent = 1000
            mock_io_stats.packets_recv = 2000

            mock_net_io_counters.return_value = {
                "eth0": mock_io_stats
            }

            # 执行测试
            result = await get_network_info(mock_request)

            # 验证结果
            assert result.success is True
            assert len(result.data) == 1

            network_info = result.data[0]
            assert network_info["interface"] == "eth0"
            assert network_info["ip_address"] == "192.168.1.100"
            assert network_info["netmask"] == "255.255.255.0"
            assert network_info["broadcast"] == "192.168.1.255"
            assert network_info["bytes_sent"] == 1024 * 1024
            assert network_info["bytes_recv"] == 2 * 1024 * 1024
            assert network_info["packets_sent"] == 1000
            assert network_info["packets_recv"] == 2000

        @patch('src.api.routers.system.psutil.net_if_addrs')
        async def test_get_network_info_error(self, mock_net_if_addrs, mock_request):
            """测试获取网络信息时发生异常"""
            from src.api.routers.system import get_network_info

            # 设置异常
            mock_net_if_addrs.side_effect = Exception("Network error")

            # 执行测试并验证异常
            with pytest.raises(HTTPException) as exc_info:
                await get_network_info(mock_request)

            assert exc_info.value.status_code == 500
            assert "获取网络信息失败: Network error" in str(exc_info.value.detail)

    class TestGetProcessInfo:
        """测试获取进程信息接口"""

        @patch('src.api.routers.system.psutil.process_iter')
        @patch('src.api.routers.system.datetime')
        async def test_get_process_info_success(self, mock_datetime, mock_process_iter, mock_request):
            """测试成功获取进程信息"""
            from src.api.routers.system import get_process_info

            # 设置模拟进程数据
            mock_process1 = Mock()
            mock_process1.info = {
                'pid': 1234,
                'name': 'python',
                'status': 'running',
                'cpu_percent': 15.5,
                'memory_percent': 8.2,
                'create_time': 1672531200.0
            }

            mock_process2 = Mock()
            mock_process2.info = {
                'pid': 5678,
                'name': 'chrome',
                'status': 'sleeping',
                'cpu_percent': 25.3,
                'memory_percent': 12.1,
                'create_time': 1672534800.0
            }

            mock_process_iter.return_value = [mock_process1, mock_process2]

            # 设置模拟时间
            mock_datetime.fromtimestamp.side_effect = [
                Mock(strftime=Mock(return_value="2023-01-01 00:00:00")),
                Mock(strftime=Mock(return_value="2023-01-01 01:00:00"))
            ]

            # 执行测试
            result = await get_process_info(mock_request, limit=10)

            # 验证结果 - 按 CPU 使用率降序排列
            assert result.success is True
            assert len(result.data) == 2

            # 第一个进程应该是 CPU 使用率更高的 chrome
            process1 = result.data[0]
            assert process1["name"] == "chrome"
            assert process1["cpu_percent"] == 25.3

            # 第二个进程是 python
            process2 = result.data[1]
            assert process2["name"] == "python"
            assert process2["cpu_percent"] == 15.5

        @patch('src.api.routers.system.psutil.process_iter')
        async def test_get_process_info_with_limit(self, mock_process_iter, mock_request):
            """测试限制返回进程数量"""
            from src.api.routers.system import get_process_info

            # 创建多个模拟进程
            processes = []
            for i in range(5):
                mock_process = Mock()
                mock_process.info = {
                    'pid': 1000 + i,
                    'name': f'process{i}',
                    'status': 'running',
                    'cpu_percent': float(i * 10),
                    'memory_percent': 5.0,
                    'create_time': 1672531200.0
                }
                processes.append(mock_process)

            mock_process_iter.return_value = processes

            # 执行测试，限制返回 3 个进程
            result = await get_process_info(mock_request, limit=3)

            # 验证结果
            assert result.success is True
            assert len(result.data) == 3  # 应该只返回 3 个进程

        @patch('src.api.routers.system.psutil.process_iter')
        async def test_get_process_info_error(self, mock_process_iter, mock_request):
            """测试获取进程信息时发生异常"""
            from src.api.routers.system import get_process_info

            # 设置异常
            mock_process_iter.side_effect = Exception("Process error")

            # 执行测试并验证异常
            with pytest.raises(HTTPException) as exc_info:
                await get_process_info(mock_request)

            assert exc_info.value.status_code == 500
            assert "获取进程信息失败: Process error" in str(exc_info.value.detail)

    class TestSystemHealthCheck:
        """测试系统健康检查接口"""

        @patch('src.api.routers.system.psutil.cpu_percent')
        @patch('src.api.routers.system.psutil.virtual_memory')
        @patch('src.api.routers.system.psutil.disk_usage')
        @patch('src.api.routers.system.os.getloadavg')
        @patch('src.api.routers.system.datetime')
        async def test_system_health_check_healthy(self, mock_datetime, mock_getloadavg, mock_disk_usage,
                                                   mock_virtual_memory, mock_cpu_percent, mock_request):
            """测试系统健康状态正常的情况"""
            from src.api.routers.system import system_health_check

            # 设置模拟数据 - 正常状态
            mock_cpu_percent.return_value = 30.0  # CPU 使用率 30%

            mock_memory = Mock()
            mock_memory.percent = 60.0  # 内存使用率 60%
            mock_virtual_memory.return_value = mock_memory

            mock_disk = Mock()
            mock_disk.total = 100 * 1024 * 1024 * 1024  # 100GB
            mock_disk.used = 40 * 1024 * 1024 * 1024  # 40GB，使用率 40%
            mock_disk_usage.return_value = mock_disk

            mock_getloadavg.return_value = (0.5, 0.8, 1.2)

            mock_datetime.now.return_value.strftime.return_value = "2025-09-10 09:38:41"

            # 执行测试
            result = await system_health_check(mock_request)

            # 验证结果
            assert result.success is True
            assert result.data["status"] == "healthy"
            assert result.data["timestamp"] == "2025-09-10 09:38:41"
            assert result.data["metrics"]["cpu_usage_percent"] == 30.0
            assert result.data["metrics"]["memory_usage_percent"] == 60.0
            assert result.data["metrics"]["disk_usage_percent"] == 40.0
            assert result.data["metrics"]["load_average"] == (0.5, 0.8, 1.2)
            assert len(result.data["alerts"]) == 0

        @patch('src.api.routers.system.psutil.cpu_percent')
        @patch('src.api.routers.system.psutil.virtual_memory')
        @patch('src.api.routers.system.psutil.disk_usage')
        @patch('src.api.routers.system.datetime')
        async def test_system_health_check_warning(self, mock_datetime, mock_disk_usage,
                                                   mock_virtual_memory, mock_cpu_percent, mock_request):
            """测试系统健康状态警告的情况"""
            from src.api.routers.system import system_health_check

            # 设置模拟数据 - 警告状态
            mock_cpu_percent.return_value = 85.0  # CPU 使用率 85% (>80%)

            mock_memory = Mock()
            mock_memory.percent = 90.0  # 内存使用率 90% (>85%)
            mock_virtual_memory.return_value = mock_memory

            mock_disk = Mock()
            mock_disk.total = 100 * 1024 * 1024 * 1024  # 100GB
            mock_disk.used = 95 * 1024 * 1024 * 1024  # 95GB，使用率 95% (>90%)
            mock_disk_usage.return_value = mock_disk

            mock_datetime.now.return_value.strftime.return_value = "2025-09-10 09:38:41"

            # 执行测试
            result = await system_health_check(mock_request)

            # 验证结果
            assert result.success is True
            assert result.data["status"] == "warning"
            assert len(result.data["alerts"]) == 3
            assert "CPU使用率过高" in result.data["alerts"]
            assert "内存使用率过高" in result.data["alerts"]
            assert "磁盘使用率过高" in result.data["alerts"]

        @patch('src.api.routers.system.psutil.cpu_percent')
        async def test_system_health_check_error(self, mock_cpu_percent, mock_request):
            """测试系统健康检查时发生异常"""
            from src.api.routers.system import system_health_check

            # 设置异常
            mock_cpu_percent.side_effect = Exception("Health check error")

            # 执行测试并验证异常
            with pytest.raises(HTTPException) as exc_info:
                await system_health_check(mock_request)

            assert exc_info.value.status_code == 500
            assert "系统健康检查失败: Health check error" in str(exc_info.value.detail)

    class TestHTTPEndpoints:
        """测试 HTTP 端点"""

        def test_system_info_endpoint(self, client):
            """测试系统信息端点"""
            with patch('src.api.routers.system.platform.uname') as mock_uname, \
                    patch('src.api.routers.system.psutil.boot_time') as mock_boot_time, \
                    patch('src.api.routers.system.datetime') as mock_datetime:
                # 设置模拟数据
                mock_uname_result = Mock()
                mock_uname_result.node = "test-host"
                mock_uname_result.system = "Linux"
                mock_uname_result.release = "5.15.0"
                mock_uname_result.machine = "x86_64"
                mock_uname_result.processor = "Intel"
                mock_uname.return_value = mock_uname_result

                mock_boot_time.return_value = 1672531200.0
                mock_datetime.fromtimestamp.return_value.strftime.return_value = "2023-01-01 00:00:00"
                mock_datetime.now.return_value.strftime.return_value = "2025-09-10 09:38:41"

                # 发送请求
                response = client.get("/system/info")

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["data"]["hostname"] == "test-host"

        def test_cpu_info_endpoint(self, client):
            """测试 CPU 信息端点"""
            with patch('src.api.routers.system.psutil.cpu_count') as mock_cpu_count, \
                    patch('src.api.routers.system.psutil.cpu_freq') as mock_cpu_freq, \
                    patch('src.api.routers.system.psutil.cpu_percent') as mock_cpu_percent:
                # 设置模拟数据
                mock_cpu_count.side_effect = [4, 8]
                mock_freq = Mock()
                mock_freq.max = 3000.0
                mock_freq.min = 800.0
                mock_freq.current = 2000.0
                mock_cpu_freq.return_value = mock_freq
                mock_cpu_percent.side_effect = [50.0, [10.0, 20.0, 30.0, 40.0, 15.0, 25.0, 35.0, 45.0]]

                # 发送请求
                response = client.get("/system/cpu")

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["data"]["physical_cores"] == 4
                assert data["data"]["total_cores"] == 8

        def test_memory_info_endpoint(self, client):
            """测试内存信息端点"""
            with patch('src.api.routers.system.psutil.virtual_memory') as mock_virtual_memory:
                # 设置模拟数据
                mock_memory = Mock()
                mock_memory.total = 16 * 1024 * 1024 * 1024
                mock_memory.available = 8 * 1024 * 1024 * 1024
                mock_memory.used = 8 * 1024 * 1024 * 1024
                mock_memory.percent = 50.0
                mock_memory.free = 8 * 1024 * 1024 * 1024
                mock_virtual_memory.return_value = mock_memory

                # 发送请求
                response = client.get("/system/memory")

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["data"]["percentage"] == 50.0

        def test_health_check_endpoint(self, client):
            """测试健康检查端点"""
            with patch('src.api.routers.system.psutil.cpu_percent') as mock_cpu_percent, \
                    patch('src.api.routers.system.psutil.virtual_memory') as mock_virtual_memory, \
                    patch('src.api.routers.system.psutil.disk_usage') as mock_disk_usage, \
                    patch('src.api.routers.system.datetime') as mock_datetime:
                # 设置模拟数据
                mock_cpu_percent.return_value = 25.0
                mock_memory = Mock()
                mock_memory.percent = 40.0
                mock_virtual_memory.return_value = mock_memory

                mock_disk = Mock()
                mock_disk.total = 100 * 1024 * 1024 * 1024
                mock_disk.used = 30 * 1024 * 1024 * 1024
                mock_disk_usage.return_value = mock_disk

                mock_datetime.now.return_value.strftime.return_value = "2025-09-10 09:38:41"

                # 发送请求
                response = client.get("/system/health")

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["data"]["status"] == "healthy"
                assert len(data["data"]["alerts"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
