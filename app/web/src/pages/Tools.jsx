import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Button,
  Modal,
  Typography,
  Spin,
  Empty,
  Alert,
  Tag,
  Space,
  Descriptions,
  Badge,
  Row,
  Col,
  Statistic,
  Divider,
  Tooltip
} from 'antd';
import {
  ToolOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
  UserOutlined,
  CalendarOutlined,
  TagOutlined,
  LinkOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { getTools, getToolDetails } from '../api/tools';
import { useLanguage } from '../contexts/LanguageContext';
import '../styles/Tools.css';
import ToolDetailModal from '../components/ToolDetailModal';

const { Title, Text, Paragraph } = Typography;

const Tools = () => {
  const { t } = useLanguage();

  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailModal, setDetailModal] = useState(false);
  const [selectedTool, setSelectedTool] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getTools({ include_stats: true });
      console.log('Tools API Response:', response);

      let toolsData = [];
      let statsData = {};

      if (response && response.data) {
        if (Array.isArray(response.data.tools)) {
          toolsData = response.data.tools;
        }
        if (response.data.stats) {
          statsData = response.data.stats;
        }
      }

      setTools(toolsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch tools:', error);
      setError(error.message || t('tools.fetchToolsFailed'));
      setTools([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (toolId) => {
    setDetailLoading(true);
    setDetailModal(true);
    try {
      const response = await getToolDetails(toolId);
      console.log('Tool Details Response:', response);
      setSelectedTool(response.data);
    } catch (error) {
      console.error('Failed to fetch tool details:', error);
      setSelectedTool({ error: t('tools.getDetailsFailed') });
    } finally {
      setDetailLoading(false);
    }
  };

  const handleModalClose = () => {
    setDetailModal(false);
    setSelectedTool(null);
  };

  // 获取状态图标和颜色
  const getStatusInfo = (status) => {
    const statusMap = {
      'active': { icon: <CheckCircleOutlined />, color: 'success', text: t('tools.statusTypes.active') },
      'loaded': { icon: <CheckCircleOutlined />, color: 'success', text: t('tools.statusTypes.loaded') },
      'inactive': { icon: <ExclamationCircleOutlined />, color: 'warning', text: t('tools.statusTypes.inactive') },
      'error': { icon: <CloseCircleOutlined />, color: 'error', text: t('tools.statusTypes.error') },
      'disabled': { icon: <CloseCircleOutlined />, color: 'default', text: t('tools.statusTypes.disabled') }
    };
    return statusMap[status] || { icon: <InfoCircleOutlined />, color: 'default', text: status || t('tools.statusTypes.unknown') };
  };

  // 格式化时间
  const formatTime = (timeStr) => {
    if (!timeStr) return '-';
    try {
      return new Date(timeStr).toLocaleString('zh-CN');
    } catch {
      return timeStr;
    }
  };

  // 渲染工具卡片
  const renderToolCard = (tool) => {
    const statusInfo = getStatusInfo(tool.status);

    return (
      <List.Item key={tool.id}>
        <Card
          hoverable
          className="tool-card"
          actions={[
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetails(tool.id)}
              className="tool-action-btn"
            >
              {t('tools.viewDetails')}
            </Button>
          ]}
        >
          <Card.Meta
            avatar={
              <div className="tool-avatar">
                <ToolOutlined className="tool-icon" />
                <Badge
                  status={statusInfo.color}
                  text={statusInfo.text}
                  className="tool-badge"
                />
              </div>
            }
            title={
              <div className="tool-title">
                <span>{tool.name}</span>
                <Tag color="blue" style={{ marginLeft: 8 }}>v{tool.version}</Tag>
              </div>
            }
            description={
              <div>
                <Paragraph
                  ellipsis={{ rows: 2, expandable: true }}
                  className="tool-description"
                >
                  {tool.description || t('tools.noDescription')}
                </Paragraph>

                <Space wrap size={[4, 4]} className="tool-tags">
                  {tool.tags && tool.tags.map(tag => (
                    <Tag key={tag} size="small">{tag}</Tag>
                  ))}
                </Space>

                <div className="tool-meta">
                  <Space>
                    <CalendarOutlined />
                    <span>{t('tools.registeredAt')}: {formatTime(tool.registered_at)}</span>
                  </Space>
                </div>
              </div>
            }
          />
        </Card>
      </List.Item>
    );
  };

  // 错误状态
  if (error) {
    return (
      <div className="tools-container">
        <div className="tools-content">
          <div className="tools-header">
            <Title level={2} style={{ color: 'white' }}>{t('tools.title')}</Title>
          </div>
          <Alert
            message={t('tools.fetchToolsFailed')}
            description={error}
            type="error"
            showIcon
            action={
              <Button size="small" onClick={fetchTools}>
                {t('tools.retry')}
              </Button>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="tools-container">
      <div className="tools-content">
        {/* 页面头部 */}
        <div className="tools-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Title level={2} style={{ color: 'white', margin: 0 }}>{t('tools.title')}</Title>
              <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: '14px' }}>
                {t('tools.statistics.totalCount')}: {stats.total_count || 0}
              </Text>
            </div>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchTools}
              loading={loading}
              className="tools-refresh-btn"
            >
              {t('tools.refresh')}
            </Button>
          </div>
        </div>

        {/* 统计信息 */}
        {stats && Object.keys(stats).length > 0 && (
          <Row gutter={[16, 16]} className="tools-stats-cards" style={{ marginBottom: 24 }}>
            <Col xs={12} sm={8} md={6}>
              <Card className="nuwa-glass-card">
                <Statistic
                  title={t('tools.statistics.totalCount')}
                  value={stats.total_count || 0}
                  prefix={<ToolOutlined className="stat-icon" />}
                  valueStyle={{ color: 'var(--color-info)', fontSize: '20px', fontWeight: 'bold' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={8} md={6}>
              <Card className="nuwa-glass-card">
                <Statistic
                  title={t('tools.statistics.activeCount')}
                  value={stats.active_count || 0}
                  prefix={<CheckCircleOutlined className="stat-icon" />}
                  valueStyle={{ color: 'var(--color-success)', fontSize: '20px', fontWeight: 'bold' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={8} md={6}>
              <Card className="nuwa-glass-card">
                <Statistic
                  title={t('tools.statistics.categoryCount')}
                  value={stats.category_count || 0}
                  prefix={<TagOutlined className="stat-icon" />}
                  valueStyle={{ color: 'var(--color-warning)', fontSize: '20px', fontWeight: 'bold' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={8} md={6}>
              <Card className="nuwa-glass-card">
                <Statistic
                  title={t('tools.statistics.filteredCount')}
                  value={stats.filtered_count || stats.total_count || 0}
                  prefix={<InfoCircleOutlined className="stat-icon" />}
                  valueStyle={{ color: 'var(--color-processing)', fontSize: '20px', fontWeight: 'bold' }}
                />
              </Card>
            </Col>
          </Row>
        )}

        {/* 工具列表 */}
        <Card className="tools-list-card">
          <Spin spinning={loading}>
            {!loading && (!Array.isArray(tools) || tools.length === 0) ? (
              <Empty
                description={t('tools.noToolsAvailable')}
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            ) : (
              <List
                grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
                dataSource={tools}
                renderItem={renderToolCard}
              />
            )}
          </Spin>
        </Card>

        {/* 工具详情弹窗 (提取为组件) */}
        <ToolDetailModal
          open={detailModal}
          onClose={handleModalClose}
          selectedTool={selectedTool}
          loading={detailLoading}
          t={t}
          getStatusInfo={getStatusInfo}
          formatTime={formatTime}
        />
      </div>
    </div>
  );
};

export default Tools;