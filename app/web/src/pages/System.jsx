import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Button, Typography } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { 
  getSystemInfo, 
  getCpuInfo, 
  getMemoryInfo, 
  getDiskInfo, 
  getNetworkInfo, 
  getProcessInfo 
} from '../api/system';

const { Title } = Typography;

const System = () => {
  const [systemInfo, setSystemInfo] = useState({});
  const [cpuInfo, setCpuInfo] = useState({});
  const [memoryInfo, setMemoryInfo] = useState({});
  const [diskInfo, setDiskInfo] = useState({});
  const [networkInfo, setNetworkInfo] = useState({});
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAllSystemData();
  }, []);

  const fetchAllSystemData = async () => {
    setLoading(true);
    try {
      const [
        systemRes,
        cpuRes,
        memoryRes,
        diskRes,
        networkRes,
        processRes
      ] = await Promise.all([
        getSystemInfo(),
        getCpuInfo(),
        getMemoryInfo(),
        getDiskInfo(),
        getNetworkInfo(),
        getProcessInfo(10)
      ]);

      setSystemInfo(systemRes.data || {});
      setCpuInfo(cpuRes.data || {});
      setMemoryInfo(memoryRes.data || {});
      setDiskInfo(diskRes.data || {});
      setNetworkInfo(networkRes.data || {});
      // 注意这里的变化：processRes.data.processes
      setProcesses(processRes.data?.processes || []);
    } catch (error) {
      console.error('获取系统信息失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const processColumns = [
    {
      title: 'PID',
      dataIndex: 'pid',
      key: 'pid',
    },
    {
      title: '进程名',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'CPU使用率',
      dataIndex: 'cpu_percent',
      key: 'cpu_percent',
      render: (value) => `${value}%`,
    },
    {
      title: '内存使用',
      dataIndex: 'memory_percent',
      key: 'memory_percent',
      render: (value) => `${value?.toFixed(2)}%`,
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2}>系统监控</Title>
        <Button 
          type="primary" 
          icon={<ReloadOutlined />} 
          onClick={fetchAllSystemData}
          loading={loading}
        >
          刷新数据
        </Button>
      </div>

      {/* 系统基本信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="主机名"
              value={systemInfo.hostname || '-'}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="操作系统"
              value={systemInfo.platform || '-'}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="架构"
              value={systemInfo.architecture || '-'}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="启动时间"
              value={systemInfo.boot_time || '-'}
            />
          </Card>
        </Col>
      </Row>

      {/* CPU和内存信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="CPU信息" loading={loading}>
            <Statistic
              title="CPU核心数"
              value={cpuInfo.total_cores || 0}
              style={{ marginBottom: 16 }}
            />
            <div>
              <span>CPU使用率: </span>
              <Progress 
                percent={Math.round(cpuInfo.cpu_usage || 0)} 
                size="small"
                status={cpuInfo.cpu_usage > 80 ? 'exception' : 'normal'}
              />
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="内存信息" loading={loading}>
            <Statistic
              title="总内存"
              value={Math.round((memoryInfo.total || 0) / (1024 ** 3))}
              suffix="GB"
              style={{ marginBottom: 16 }}
            />
            <div>
              <span>内存使用率: </span>
              <Progress 
                percent={Math.round(memoryInfo.percentage || 0)} 
                size="small"
                status={memoryInfo.percentage > 80 ? 'exception' : 'normal'}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* 磁盘和网络信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="磁盘信息" loading={loading}>
            {diskInfo.disks && diskInfo.disks.map((disk, index) => (
              <div key={index} style={{ marginBottom: 16 }}>
                <div style={{ marginBottom: 8 }}>
                  <strong>{disk.device}</strong> ({disk.mountpoint})
                </div>
                <Progress 
                  percent={Math.round(disk.percentage || 0)} 
                  size="small"
                  status={disk.percentage > 80 ? 'exception' : 'normal'}
                />
              </div>
            ))}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="网络信息" loading={loading}>
            <Statistic
              title="网络接口数"
              value={networkInfo.total_interfaces || 0}
              style={{ marginBottom: 16 }}
            />
            {networkInfo.interfaces && networkInfo.interfaces.slice(0, 3).map((iface, index) => (
              <div key={index} style={{ marginBottom: 8 }}>
                <div><strong>{iface.interface}</strong>: {iface.ip_address}</div>
              </div>
            ))}
          </Card>
        </Col>
      </Row>

      {/* 进程信息 */}
      <Card title="进程信息" loading={loading}>
        <Table
          dataSource={processes}
          columns={processColumns}
          pagination={{ pageSize: 10 }}
          rowKey="pid"
        />
      </Card>
    </div>
  );
};

export default System;