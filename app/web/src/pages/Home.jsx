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
import { useLanguage } from '../contexts/LanguageContext';

const Home = () => {
  const { t } = useLanguage();
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
        console.error(t('messages.loadFailed'), error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [t]);

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title={t('home.features.tools')}
              value={toolsCount}
              prefix={<ToolOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title={t('home.features.tasks')}
              value={0}
              prefix={<UnorderedListOutlined />}  
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title={t('common.status')}
              value={healthData?.success ? t('common.online') : t('common.offline')}
              prefix={healthData?.success ? 
                <CheckCircleOutlined style={{ color: '#52c41a' }} /> : 
                <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
              }
            />
          </Card>
        </Col>
      </Row>

      <Alert
        message={t('home.title')}
        description={t('home.description')}
        type="info"
        showIcon
      />
    </div>
  );
};

export default Home;