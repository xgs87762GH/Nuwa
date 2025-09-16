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

const { Title, Text, Paragraph } = Typography;

const Tools = () => {
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
      console.error('获取工具列表失败:', error);
      setError(error.message || '获取工具列表失败');
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
      console.error('获取工具详情失败:', error);
      setSelectedTool({ error: '获取详情失败' });
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
      'active': { icon: <CheckCircleOutlined />, color: 'success', text: '运行中' },
      'loaded': { icon: <CheckCircleOutlined />, color: 'success', text: '已加载' },
      'inactive': { icon: <ExclamationCircleOutlined />, color: 'warning', text: '未激活' },
      'error': { icon: <CloseCircleOutlined />, color: 'error', text: '错误' },
      'disabled': { icon: <CloseCircleOutlined />, color: 'default', text: '已禁用' }
    };
    return statusMap[status] || { icon: <InfoCircleOutlined />, color: 'default', text: status || '未知' };
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
              查看详情
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
                  {tool.description || '暂无描述'}
                </Paragraph>
                
                <Space wrap size={[4, 4]}>
                  {tool.tags && tool.tags.map(tag => (
                    <Tag key={tag} size="small">{tag}</Tag>
                  ))}
                </Space>
                
                <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                  <Space>
                    <CalendarOutlined />
                    <span>注册时间: {formatTime(tool.registered_at)}</span>
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
        <Title level={2}>工具管理</Title>
        <Alert
          message="获取工具列表失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={fetchTools}>
              重试
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
        <Title level={2}>工具管理</Title>
        <Button 
          icon={<ReloadOutlined />}
          onClick={fetchTools} 
          loading={loading}
        >
          刷新
        </Button>
      </div>

      {/* 统计信息 */}
      {stats && Object.keys(stats).length > 0 && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总工具数"
                value={stats.total_count || 0}
                prefix={<ToolOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="运行中"
                value={stats.active_count || 0}
                valueStyle={{ color: '#3f8600' }}
                prefix={<CheckCircleOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="分类数"
                value={stats.category_count || 0}
                prefix={<TagOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="已筛选"
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
              description="暂无可用工具" 
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
            <span>{selectedTool?.name || '工具详情'}</span>
            {selectedTool?.version && <Tag color="blue">v{selectedTool.version}</Tag>}
          </Space>
        }
        open={detailModal}
        onCancel={handleModalClose}
        footer={[
          <Button key="close" onClick={handleModalClose}>
            关闭
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
                  <Descriptions title="基本信息" bordered column={2} size="small">
                    <Descriptions.Item label="工具名称">{selectedTool.name}</Descriptions.Item>
                    <Descriptions.Item label="版本">{selectedTool.version}</Descriptions.Item>
                    <Descriptions.Item label="状态">
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
                    <Descriptions.Item label="是否启用">
                      {selectedTool.is_enabled ? 
                        <Tag color="success">已启用</Tag> : 
                        <Tag color="default">未启用</Tag>
                      }
                    </Descriptions.Item>
                    <Descriptions.Item label="注册时间" span={2}>
                      {formatTime(selectedTool.registered_at)}
                    </Descriptions.Item>
                    <Descriptions.Item label="描述" span={2}>
                      <Paragraph>{selectedTool.description || '暂无描述'}</Paragraph>
                    </Descriptions.Item>
                  </Descriptions>

                  {/* 标签 */}
                  {selectedTool.tags && selectedTool.tags.length > 0 && (
                    <>
                      <Divider>标签</Divider>
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
                      <Divider>详细信息</Divider>
                      <Descriptions bordered column={1} size="small">
                        {selectedTool.metadata.author && (
                          <Descriptions.Item label="作者">
                            <Space>
                              <UserOutlined />
                              {selectedTool.metadata.author}
                            </Space>
                          </Descriptions.Item>
                        )}
                        {selectedTool.metadata.license && (
                          <Descriptions.Item label="许可证">
                            {selectedTool.metadata.license}
                          </Descriptions.Item>
                        )}
                        {selectedTool.metadata.keywords && selectedTool.metadata.keywords.length > 0 && (
                          <Descriptions.Item label="关键词">
                            <Space wrap>
                              {selectedTool.metadata.keywords.map(keyword => (
                                <Tag key={keyword} size="small">{keyword}</Tag>
                              ))}
                            </Space>
                          </Descriptions.Item>
                        )}
                        {selectedTool.metadata.requirements && selectedTool.metadata.requirements.length > 0 && (
                          <Descriptions.Item label="依赖项">
                            <Space direction="vertical" size="small" style={{ width: '100%' }}>
                              {selectedTool.metadata.requirements.map((req, index) => (
                                <Tag key={index} style={{ marginBottom: 4 }}>{req}</Tag>
                              ))}
                            </Space>
                          </Descriptions.Item>
                        )}
                        {selectedTool.metadata.urls && Object.keys(selectedTool.metadata.urls).length > 0 && (
                          <Descriptions.Item label="相关链接">
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
                      查看原始数据 (调试)
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