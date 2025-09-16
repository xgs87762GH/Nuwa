import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Alert } from 'antd';
import { 
  ToolOutlined, 
  UnorderedListOutlined,  // 使用 UnorderedListOutlined 替代 TasksOutlined
  CheckCircleOutlined, 
  ExclamationCircleOutlined 
} from '@ant-design/icons';
import { getSystemHealth } from '../api/system';
import { getToolsStatistics } from '../api/tools';  // 从正确的位置导入

const Home = () => {
  const [healthData, setHealthData] = useState(null);
  const [toolsCount, setToolsCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, toolsRes] = await Promise.all([
          getSystemHealth(),
          getToolsStatistics()
        ]);
        setHealthData(healthRes);
        setToolsCount(toolsRes.data?.total || 0);
      } catch (error) {
        console.error('获取数据失败:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="可用工具"
              value={toolsCount}
              prefix={<ToolOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="活跃任务"
              value={0}
              prefix={<UnorderedListOutlined />}  
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="系统状态"
              value={healthData?.success ? "正常" : "异常"}
              prefix={healthData?.success ? 
                <CheckCircleOutlined style={{ color: '#52c41a' }} /> : 
                <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
              }
            />
          </Card>
        </Col>
      </Row>

      <Alert
        message="欢迎使用 Nuwa 智能AI插件管理平台"
        description="这是一个强大的AI插件管理和任务调度平台，可以帮助您管理各种AI工具和自动化任务。"
        type="info"
        showIcon
      />
    </div>
  );
};

export default Home;