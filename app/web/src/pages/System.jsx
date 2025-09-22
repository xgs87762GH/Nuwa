import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Button, Typography, Select, Tag, message, Space, Divider } from 'antd';
import { ReloadOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { 
  getSystemInfo, 
  getCpuInfo, 
  getMemoryInfo, 
  getDiskInfo, 
  getNetworkInfo, 
  getProcessInfo 
} from '../api/system';
import { useLanguage } from '../contexts/LanguageContext';

const { Title } = Typography;
const { Option } = Select;

const System = () => {
  const { t } = useLanguage();
  
  const [systemInfo, setSystemInfo] = useState({});
  const [cpuInfo, setCpuInfo] = useState({});
  const [memoryInfo, setMemoryInfo] = useState({});
  const [diskInfo, setDiskInfo] = useState({});
  const [networkInfo, setNetworkInfo] = useState({});
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // AI provider related states
  const [aiProviders, setAiProviders] = useState([]);
  const [currentProvider, setCurrentProvider] = useState(null);
  const [loadingProviders, setLoadingProviders] = useState(false);

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
      // Note the change here: processRes.data.processes
      setProcesses(processRes.data?.processes || []);
    } catch (error) {
      console.error('Failed to get system information:', error);
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
      title: t('system.processName'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('system.cpuUsagePercent'),
      dataIndex: 'cpu_percent',
      key: 'cpu_percent',
      render: (value) => `${value}%`,
    },
    {
      title: t('system.memoryUsageAmount'),
      dataIndex: 'memory_percent',
      key: 'memory_percent',
      render: (value) => `${value?.toFixed(2)}%`,
    },
  ];

  return (
    <div>
      {/* 系统基本信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title={t('system.hostname')}
              value={systemInfo.hostname || '-'}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title={t('system.operatingSystem')}
              value={systemInfo.platform || '-'}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title={t('system.architecture')}
              value={systemInfo.architecture || '-'}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title={t('system.bootTime')}
              value={systemInfo.boot_time || '-'}
            />
          </Card>
        </Col>
      </Row>

      {/* CPU和内存信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title={t('system.cpuInfo')} loading={loading}>
            <Statistic
              title={t('system.cpuCores')}
              value={cpuInfo.total_cores || 0}
              style={{ marginBottom: 16 }}
            />
            <div>
              <span>{t('system.cpuUsage')}: </span>
              <Progress 
                percent={Math.round(cpuInfo.cpu_usage || 0)} 
                size="small"
                status={cpuInfo.cpu_usage > 80 ? 'exception' : 'normal'}
              />
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title={t('system.memoryInfo')} loading={loading}>
            <Statistic
              title={t('system.totalMemory')}
              value={Math.round((memoryInfo.total || 0) / (1024 ** 3))}
              suffix="GB"
              style={{ marginBottom: 16 }}
            />
            <div>
              <span>{t('system.memoryUsage')}: </span>
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
          <Card title={t('system.diskUsage')} loading={loading}>
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
          <Card title={t('system.networkInfo')} loading={loading}>
            <Statistic
              title={t('system.networkInterfaces')}
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
      <Card title={t('system.processInfo')} loading={loading}>
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