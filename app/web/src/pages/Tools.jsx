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
          style={{ width: '100%' }}
          actions={[
            <Button 
              type="link" 
              icon={<EyeOutlined />}
              onClick={() => handleViewDetails(tool.id)}
            >
              {t('tools.viewDetails')}
            </Button>
          ]}
        >
          <Card.Meta
            avatar={
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <ToolOutlined style={{ fontSize: 32, color: '#1890ff', marginBottom: 8 }} />
                <Badge 
                  status={statusInfo.color} 
                  text={statusInfo.text}
                  style={{ fontSize: 12 }}
                />
              </div>
            }
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{tool.name}</span>
                <Tag color="blue">v{tool.version}</Tag>
              </div>
            }
            description={
              <div>
                <Paragraph 
                  ellipsis={{ rows: 2, expandable: true }}
                  style={{ marginBottom: 12 }}
                >
                  {tool.description || t('tools.noDescription')}
                </Paragraph>
                
                <Space wrap size={[4, 4]}>
                  {tool.tags && tool.tags.map(tag => (
                    <Tag key={tag} size="small">{tag}</Tag>
                  ))}
                </Space>
                
                <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
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
      <div>
        <Title level={2}>{t('tools.title')}</Title>
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
    );
  }

  return (
    <div>
      {/* 页面头部 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2}>{t('tools.title')}</Title>
        <Button 
          icon={<ReloadOutlined />}
          onClick={fetchTools} 
          loading={loading}
        >
          {t('tools.refresh')}
        </Button>
      </div>

      {/* 统计信息 */}
      {stats && Object.keys(stats).length > 0 && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title={t('tools.statistics.totalCount')}
                value={stats.total_count || 0}
                prefix={<ToolOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title={t('tools.statistics.activeCount')}
                value={stats.active_count || 0}
                valueStyle={{ color: '#3f8600' }}
                prefix={<CheckCircleOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title={t('tools.statistics.categoryCount')}
                value={stats.category_count || 0}
                prefix={<TagOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title={t('tools.statistics.filteredCount')}
                value={stats.filtered_count || stats.total_count || 0}
                prefix={<InfoCircleOutlined />}
              />
            </Card>
          </Col>
        </Row>
      )}
      
      {/* 工具列表 */}
      <Card>
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

      {/* 工具详情弹窗 */}
      <Modal
        title={
          <Space>
            <ToolOutlined />
            <span>{selectedTool?.name || t('tools.toolDetails')}</span>
            {selectedTool?.version && <Tag color="blue">v{selectedTool.version}</Tag>}
          </Space>
        }
        open={detailModal}
        onCancel={handleModalClose}
        footer={[
          <Button key="close" onClick={handleModalClose}>
            {t('tools.close')}
          </Button>
        ]}
        width={800}
      >
        <Spin spinning={detailLoading}>
          {selectedTool && (
            <div>
              {selectedTool.error ? (
                <Alert message={selectedTool.error} type="error" />
              ) : (
                <div>
                  {/* 基本信息 */}
                  <Descriptions title={t('tools.basicInfo')} bordered column={2} size="small">
                    <Descriptions.Item label={t('tools.toolName')}>{selectedTool.name}</Descriptions.Item>
                    <Descriptions.Item label={t('tools.version')}>{selectedTool.version}</Descriptions.Item>
                    <Descriptions.Item label={t('tools.status')}>
                      {(() => {
                        const statusInfo = getStatusInfo(selectedTool.status);
                        return (
                          <Badge 
                            status={statusInfo.color} 
                            text={statusInfo.text}
                          />
                        );
                      })()}
                    </Descriptions.Item>
                    <Descriptions.Item label={t('tools.enabled')}>
                      {selectedTool.is_enabled ? 
                        <Tag color="success">{t('tools.statusTypes.enabled')}</Tag> : 
                        <Tag color="default">{t('tools.statusTypes.notEnabled')}</Tag>
                      }
                    </Descriptions.Item>
                    <Descriptions.Item label={t('tools.registeredAt')} span={2}>
                      {formatTime(selectedTool.registered_at)}
                    </Descriptions.Item>
                    <Descriptions.Item label={t('tools.description')} span={2}>
                      <Paragraph>{selectedTool.description || t('tools.noDescription')}</Paragraph>
                    </Descriptions.Item>
                  </Descriptions>

                  {/* 标签 */}
                  {selectedTool.tags && selectedTool.tags.length > 0 && (
                    <>
                      <Divider>{t('tools.tags')}</Divider>
                      <Space wrap>
                        {selectedTool.tags.map(tag => (
                          <Tag key={tag} icon={<TagOutlined />}>{tag}</Tag>
                        ))}
                      </Space>
                    </>
                  )}

                  {/* 元数据 */}
                  {selectedTool.metadata && (
                    <>
                      <Divider>{t('tools.detailInfo')}</Divider>
                      <Descriptions bordered column={1} size="small">
                        {selectedTool.metadata.author && (
                          <Descriptions.Item label={t('tools.author')}>
                            <Space>
                              <UserOutlined />
                              {selectedTool.metadata.author}
                            </Space>
                          </Descriptions.Item>
                        )}
                        {selectedTool.metadata.license && (
                          <Descriptions.Item label={t('tools.license')}>
                            {selectedTool.metadata.license}
                          </Descriptions.Item>
                        )}
                        {selectedTool.metadata.keywords && selectedTool.metadata.keywords.length > 0 && (
                          <Descriptions.Item label={t('tools.keywords')}>
                            <Space wrap>
                              {selectedTool.metadata.keywords.map(keyword => (
                                <Tag key={keyword} size="small">{keyword}</Tag>
                              ))}
                            </Space>
                          </Descriptions.Item>
                        )}
                        {selectedTool.metadata.requirements && selectedTool.metadata.requirements.length > 0 && (
                          <Descriptions.Item label={t('tools.dependencies')}>
                            <Space direction="vertical" size="small" style={{ width: '100%' }}>
                              {selectedTool.metadata.requirements.map((req, index) => (
                                <Tag key={index} style={{ marginBottom: 4 }}>{req}</Tag>
                              ))}
                            </Space>
                          </Descriptions.Item>
                        )}
                        {selectedTool.metadata.urls && Object.keys(selectedTool.metadata.urls).length > 0 && (
                          <Descriptions.Item label={t('tools.relatedLinks')}>
                            <Space direction="vertical" size="small">
                              {Object.entries(selectedTool.metadata.urls).map(([key, url]) => (
                                <div key={key}>
                                  <LinkOutlined style={{ marginRight: 8 }} />
                                  <a href={url} target="_blank" rel="noopener noreferrer">
                                    {key}: {url}
                                  </a>
                                </div>
                              ))}
                            </Space>
                          </Descriptions.Item>
                        )}
                      </Descriptions>
                    </>
                  )}

                  {/* 原始数据（调试用） */}
                  <details style={{ marginTop: 16 }}>
                    <summary style={{ cursor: 'pointer', color: '#666' }}>
                      {t('tools.viewRawData')}
                    </summary>
                    <pre style={{ 
                      background: '#f5f5f5', 
                      padding: '12px', 
                      borderRadius: '4px',
                      overflow: 'auto',
                      maxHeight: '300px',
                      marginTop: '8px',
                      fontSize: '12px'
                    }}>
                      {JSON.stringify(selectedTool, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </div>
          )}
        </Spin>
      </Modal>
    </div>
  );
};

export default Tools;