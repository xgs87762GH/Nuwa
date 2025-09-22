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
import { 
  getAllProviders, 
  getCurrentProvider, 
  setDefaultProvider 
} from '../api/ai';
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

  // Fetch AI provider information
  const fetchAIProviders = async () => {
    setLoadingProviders(true);
    try {
      const [providersRes, currentProviderRes] = await Promise.all([
        getAllProviders(),
        getCurrentProvider()
      ]);

      if (providersRes.success && providersRes.data) {
        setAiProviders(providersRes.data.providers || []);
      }

      if (currentProviderRes.success && currentProviderRes.data) {
        setCurrentProvider(currentProviderRes.data);
      }
    } catch (error) {
      console.error('Failed to fetch AI provider information:', error);
      message.error(t('messages.loadProvidersFailed'));
    } finally {
      setLoadingProviders(false);
    }
  };

  useEffect(() => {
    fetchAllSystemData();
    fetchAIProviders();
  }, [fetchAIProviders]);

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

  // Switch AI provider
  const handleProviderChange = async (providerType) => {
    try {
      const response = await setDefaultProvider(providerType);
      if (response.success) {
        message.success(t('messages.providerSwitchSuccess'));
        fetchAIProviders(); // Refresh current provider information
      } else {
        message.error(response.message || 'Failed to switch AI provider');
      }
    } catch (error) {
      console.error('Failed to switch AI provider:', error);
      message.error('Failed to switch AI provider');
    }
  };

  // Refresh AI provider information
  const refreshAIProviders = () => {
    fetchAIProviders();
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2}>{t('system.title')}</Title>
        <Button 
          icon={<ReloadOutlined />}
          onClick={fetchAllSystemData} 
          loading={loading}
        >
          {t('system.refreshData')}
        </Button>
      </div>

      {/* 系统配置 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {/* AI提供商设置 */}
        <Col span={12}>
          <Card 
            title={
              <Space>
                <ThunderboltOutlined />
                {t('system.aiProviderSettings')}
              </Space>
            }
            loading={loadingProviders}
            extra={
              <Button 
                icon={<ReloadOutlined />} 
                size="small" 
                onClick={refreshAIProviders}
              >
                {t('system.refresh')}
              </Button>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ marginBottom: 16 }}>
                <div style={{ marginBottom: 8 }}>
                  <strong>{t('system.currentProvider')}:</strong>
                </div>
                {currentProvider ? (
                  <Tag color="blue" style={{ fontSize: '14px', padding: '4px 8px' }}>
                    {currentProvider.type?.toUpperCase() || 'N/A'}
                  </Tag>
                ) : (
                  <Tag color="red">未设置</Tag>
                )}
              </div>
              
              <Divider style={{ margin: '12px 0' }} />
              
              <div>
                <div style={{ marginBottom: 8 }}>
                  <strong>{t('system.selectProvider')}:</strong>
                </div>
                <Select
                  style={{ width: '100%' }}
                  placeholder={t('system.selectAIProvider')}
                  value={currentProvider?.type}
                  onChange={handleProviderChange}
                  loading={loadingProviders}
                >
                  {aiProviders.map(provider => (
                    <Option key={provider.type} value={provider.type}>
                      <Space>
                        <Tag 
                          size="small" 
                          color={provider.status === 'active' ? 'green' : 'orange'}
                        >
                          {provider.status === 'active' ? '可用' : '不可用'}
                        </Tag>
                        {provider.type.toUpperCase()}
                      </Space>
                    </Option>
                  ))}
                </Select>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

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
          <Card title="内存信息" loading={loading}>
            <Statistic
              title="总内存"
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