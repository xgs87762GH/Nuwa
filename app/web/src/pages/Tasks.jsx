import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import {
  Card,
  Table,
  Tag,
  Button,
  Select,
  Input,
  Space,
  message,
  Typography,
  Switch,
  Row,
  Col,
  Drawer,
  Badge,
  Tooltip,
  Empty,
  Statistic
} from 'antd';
import { useLanguage } from '../contexts/LanguageContext';
import {
  ReloadOutlined,
  SearchOutlined,
  SyncOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  DeleteOutlined,
  SettingOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  TeamOutlined,
  TrophyOutlined,
  FireOutlined,
  BugOutlined
} from '@ant-design/icons';
import { getTasksList } from '../api/tasks';
import {
  TASK_STATUS,
  TASK_STATUS_LABELS,
  TASK_STATUS_COLORS
} from '../utils/constants';
import './Tasks.css';

const { Title, Text } = Typography;
const { Option } = Select;

const Tasks = () => {
  const { t } = useLanguage();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [filters, setFilters] = useState({
    status: null,
    task_id: '',
    description: ''
  });
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [taskDetailVisible, setTaskDetailVisible] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const refreshTimerRef = useRef(null);

  // Load task list
  const loadTasks = useCallback(async (page = pagination.current, pageSize = pagination.pageSize, currentFilters = filters) => {
    setLoading(true);
    try {
      const params = {
        page,
        size: pageSize,
        ...currentFilters
      };
      
      // Filter out empty values
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      const response = await getTasksList(params);
      
      if (response?.success) {
        setTasks(response.data.items || []);
        setPagination({
          current: parseInt(response.data.page) || 1,
          pageSize: parseInt(response.data.size) || 10,
          total: parseInt(response.data.total) || 0
        });
      } else {
        message.error(response?.message || t('tasks.loadTasksFailed'));
      }
    } catch (error) {
      console.error('Load tasks error:', error);
      message.error(t('tasks.loadTasksFailed'));
    } finally {
      setLoading(false);
    }
  }, [filters, pagination, t]);

  // Clear refresh timer
  const clearRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearInterval(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
  }, []);

  // Auto refresh logic
  useEffect(() => {
    clearRefreshTimer();
    if (autoRefresh) {
      refreshTimerRef.current = setInterval(() => {
        loadTasks();
      }, 5000);
    }
    return clearRefreshTimer;
  }, [autoRefresh, loadTasks, clearRefreshTimer]);

  // Manual refresh
  const handleRefresh = () => {
    loadTasks();
  };

  // Handle pagination change
  const handleTableChange = (paginationInfo) => {
    setPagination(prev => ({
      ...prev,
      current: paginationInfo.current,
      pageSize: paginationInfo.pageSize
    }));
    loadTasks(paginationInfo.current, paginationInfo.pageSize);
  };

  // Handle filter changes
  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, current: 1 }));
    loadTasks(1, pagination.pageSize, newFilters);
  };

  // Toggle auto refresh
  const handleAutoRefreshToggle = (checked) => {
    setAutoRefresh(checked);
  };

  // View task details
  const handleViewTask = (task) => {
    setSelectedTask(task);
    setTaskDetailVisible(true);
  };

  // Calculate statistics
  const taskStats = React.useMemo(() => {
    const stats = {
      total: tasks.length,
      running: 0,
      completed: 0,
      failed: 0,
      waiting: 0
    };
    
    tasks.forEach(task => {
      switch (task.status) {
        case 'running':
          stats.running++;
          break;
        case 'completed':
        case 'success':
          stats.completed++;
          break;
        case 'failed':
          stats.failed++;
          break;
        case 'waiting':
        case 'pending':
          stats.waiting++;
          break;
        default:
          stats.waiting++;
          break;
      }
    });
    
    return stats;
  }, [tasks]);

  // Render statistics cards
  const renderStatsCards = () => (
    <Row gutter={[16, 16]} className="stats-cards">
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title={t('tasks.totalTasks')}
            value={taskStats.total}
            prefix={<TeamOutlined className="stat-icon total" />}
            valueStyle={{ color: '#3f8bff', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title={t('tasks.activeTasks')}
            value={taskStats.running}
            prefix={<FireOutlined className="stat-icon running" />}
            valueStyle={{ color: '#ff9500', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title={t('tasks.completedTasks')}
            value={taskStats.completed}
            prefix={<TrophyOutlined className="stat-icon completed" />}
            valueStyle={{ color: '#52c41a', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title={t('tasks.failedTasks')}
            value={taskStats.failed + taskStats.waiting}
            prefix={<BugOutlined className="stat-icon failed" />}
            valueStyle={{ color: '#ff4d4f', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
    </Row>
  );

  // Format time
  const formatTime = (timeString) => {
    if (!timeString) return '-';
    try {
      const date = new Date(timeString);
      if (isNaN(date.getTime())) return '-';
      // Use current language for time formatting
      const locale = t('common.locale') === 'zh' ? 'zh-CN' : 'en-US';
      return date.toLocaleString(locale);
    } catch (error) {
      return '-';
    }
  };

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
      case 'waiting':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      case 'running':
        return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      case 'success':
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  // Get priority tag
  const getPriorityTag = (priority) => {
    const colors = ['default', 'blue', 'orange', 'red'];
    const labels = [
      t('tasks.priority.normal'), 
      t('tasks.priority.low'), 
      t('tasks.priority.medium'), 
      t('tasks.priority.high')
    ];
    return (
      <Tag color={colors[priority] || 'default'}>
        {labels[priority] || t('tasks.priority.normal')}
      </Tag>
    );
  };

  // Table columns definition
  const columns = [
    {
      title: t('tasks.taskId'),
      dataIndex: 'task_id',
      key: 'task_id',
      width: 140,
      ellipsis: true,
      align: 'left',
      render: (text) => (
        <Tooltip title={text}>
          <Text 
            code 
            style={{ 
              fontSize: '11px', 
              fontFamily: 'Consolas, Monaco, monospace',
              background: 'rgba(255, 255, 255, 0.1)',
              padding: '2px 6px',
              borderRadius: '4px',
              color: '#40a9ff'
            }}
          >
            {text ? text.substring(0, 8) + '...' : '-'}
          </Text>
        </Tooltip>
      )
    },
    {
      title: t('tasks.status.title'),
      dataIndex: 'status',
      key: 'status',
      width: 110,
      align: 'center',
      render: (status) => (
        <Tag 
          color={TASK_STATUS_COLORS[status] || 'default'}
          icon={getStatusIcon(status)}
          style={{ 
            minWidth: '80px', 
            textAlign: 'center',
            fontWeight: '500'
          }}
        >
          {t(TASK_STATUS_LABELS[status]) || status}
        </Tag>
      )
    },
    {
      title: t('tasks.taskDescription'),
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      align: 'left',
      render: (text) => (
        <Tooltip title={text}>
          <Text 
            style={{ 
              maxWidth: '200px',
              display: 'inline-block',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {text || '-'}
          </Text>
        </Tooltip>
      )
    },
    {
      title: t('tasks.priority.title'),
      dataIndex: 'priority',
      key: 'priority',
      width: 90,
      align: 'center',
      render: (priority) => getPriorityTag(priority)
    },
    {
      title: t('tasks.createdAt'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      align: 'center',
      render: (text) => (
        <Text style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.7)' }}>
          {formatTime(text)}
        </Text>
      )
    },
    {
      title: t('tasks.startedAt'),
      dataIndex: 'started_at',
      key: 'started_at',
      width: 150,
      align: 'center',
      render: (text) => (
        <Text style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.7)' }}>
          {formatTime(text)}
        </Text>
      )
    },
    {
      title: t('tasks.finishedAt'),
      dataIndex: 'finished_at',
      key: 'finished_at',
      width: 150,
      align: 'center',
      render: (text) => (
        <Text style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.7)' }}>
          {formatTime(text)}
        </Text>
      )
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 140,
      align: 'center',
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title={t('tasks.actions.view')}>
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewTask(record)}
              style={{
                color: '#40a9ff',
                background: 'rgba(64, 169, 255, 0.1)',
                border: 'none'
              }}
            />
          </Tooltip>
          {record.status === 'pending' && (
            <Tooltip title={t('tasks.actions.start')}>
              <Button
                type="text"
                size="small"
                icon={<PlayCircleOutlined />}
                style={{ 
                  color: '#52c41a',
                  background: 'rgba(82, 196, 26, 0.1)'
                }}
              />
            </Tooltip>
          )}
          {record.status === 'running' && (
            <Tooltip title={t('tasks.actions.pause')}>
              <Button
                type="text"
                size="small"
                icon={<PauseCircleOutlined />}
                style={{ 
                  color: '#faad14',
                  background: 'rgba(250, 173, 20, 0.1)'
                }}
              />
            </Tooltip>
          )}
          <Tooltip title={t('tasks.actions.delete')}>
            <Button
              type="text"
              size="small"
              icon={<DeleteOutlined />}
              style={{
                color: '#ff4d4f',
                background: 'rgba(255, 77, 79, 0.1)'
              }}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  // 组件挂载时加载数据
  useEffect(() => {
    loadTasks();
    // eslint-disable-next-line
  }, []);

  // 组件卸载时清理定时器
  useEffect(() => clearRefreshTimer, [clearRefreshTimer]);

  return (
    <div className="nuwa-container">
      <div className="nuwa-content">

        {/* 统计卡片 */}
        <div style={{ marginBottom: 16 }}>
          {renderStatsCards()}
        </div>

        {/* Filters and actions */}
        <Card className="nuwa-glass-card" style={{ marginBottom: 16 }}>
          <Row gutter={[16, 16]} align="middle">
            <Col xl={5} lg={8} md={10} sm={12} xs={24}>
              <Space>
                <Text strong style={{ color: 'var(--text-primary)' }}>{t('tasks.status.title')}:</Text>
                <Select
                  placeholder={t('tasks.selectStatus')}
                  allowClear
                  style={{ width: 120 }}
                  value={filters.status}
                  onChange={(value) => handleFiltersChange({ ...filters, status: value })}
                  className="nuwa-input"
                >
                  {Object.entries(TASK_STATUS).map(([key, value]) => (
                    <Option key={value} value={value}>
                      <Space>
                        {getStatusIcon(value)}
                        <Tag color={TASK_STATUS_COLORS[value]} style={{ margin: 0 }}>
                          {t(TASK_STATUS_LABELS[value])}
                        </Tag>
                      </Space>
                    </Option>
                  ))}
                </Select>
              </Space>
            </Col>
            <Col xl={5} lg={8} md={10} sm={12} xs={24}>
              <Space>
                <Text strong>{t('tasks.taskId')}:</Text>
                <Input
                  placeholder={t('tasks.inputTaskId')}
                  style={{ width: 140 }}
                  value={filters.task_id}
                  onChange={(e) => handleFiltersChange({ ...filters, task_id: e.target.value })}
                  prefix={<SearchOutlined />}
                />
              </Space>
            </Col>
            
            <Col xl={5} lg={8} md={10} sm={12} xs={24}>
              <Space>
                <Text strong>{t('tasks.description')}:</Text>
                <Input
                  placeholder={t('tasks.inputDescription')}
                  style={{ width: 140 }}
                  value={filters.description}
                  onChange={(e) => handleFiltersChange({ ...filters, description: e.target.value })}
                  prefix={<SearchOutlined />}
                />
              </Space>
            </Col>

            <Col xl={9} lg={8} md={24} sm={24} xs={24}>
              <Space wrap>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={handleRefresh}
                  loading={loading}
                >
                  {t('common.refresh')}
                </Button>

                <Space>
                  <Text>{t('tasks.autoRefresh')}:</Text>
                  <Switch
                    checked={autoRefresh}
                    onChange={handleAutoRefreshToggle}
                    checkedChildren={<SyncOutlined />}
                    unCheckedChildren={t('common.off')}
                  />
                </Space>
              </Space>
            </Col>
          </Row>
        </Card>

      {/* 任务列表 */}
      <Card className="nuwa-glass-card task-list-card">
        <div className="task-table-container">
          <Table
            columns={columns}
            dataSource={tasks}
            loading={loading}
            pagination={{
              ...pagination,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) =>
                t('pagination.showTotal', { start: range[0], end: range[1], total }),
              pageSizeOptions: ['10', '20', '50', '100'],
              size: 'small',
              style: { marginTop: '16px' }
            }}
            onChange={handleTableChange}
            rowKey="task_id"
            scroll={{ x: 1100 }}
            size="middle"
            bordered={false}
            showHeader={true}
            locale={{
              emptyText: (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description={
                    <span style={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                      {t('tasks.noTasksData')}
                    </span>
                  }
                  style={{ 
                    padding: '60px 20px',
                    background: 'transparent'
                  }}
                />
              )
            }}
            rowClassName={(record, index) => 
              `task-row ${index % 2 === 0 ? 'even' : 'odd'}`
            }
          />
        </div>
      </Card>

      {/* Task Details Drawer */}
      <Drawer
        title={t('tasks.taskDetails')}
        open={taskDetailVisible}
        onClose={() => setTaskDetailVisible(false)}
        width={600}
      >
        {selectedTask && (
          <div>
            <Card size="small" className="nuwa-glass-card" style={{ marginBottom: 16 }}>
              <Row gutter={[16, 8]}>
                <Col span={24}>
                  <Space>
                    <Text strong>{t('tasks.taskId')}:</Text>
                    <Text code>{selectedTask.task_id}</Text>
                  </Space>
                </Col>
                <Col span={12}>
                  <Space>
                    <Text strong>{t('tasks.status.title')}:</Text>
                    <Tag 
                      color={TASK_STATUS_COLORS[selectedTask.status]}
                      icon={getStatusIcon(selectedTask.status)}
                    >
                      {t(TASK_STATUS_LABELS[selectedTask.status])}
                    </Tag>
                  </Space>
                </Col>
                <Col span={12}>
                  <Space>
                    <Text strong>{t('tasks.priority.title')}:</Text>
                    {getPriorityTag(selectedTask.priority)}
                  </Space>
                </Col>
                <Col span={24}>
                  <Text strong>{t('tasks.taskDescription')}:</Text>
                  <div style={{ margin: '8px 0' }}>
                    {selectedTask.description}
                  </div>
                </Col>
                <Col span={8}>
                  <Space>
                    <Text strong>{t('tasks.createdAt')}:</Text>
                    <Text>{formatTime(selectedTask.created_at)}</Text>
                  </Space>
                </Col>
                <Col span={8}>
                  <Space>
                    <Text strong>{t('tasks.startedAt')}:</Text>
                    <Text>{formatTime(selectedTask.started_at)}</Text>
                  </Space>
                </Col>
                <Col span={8}>
                  <Space>
                    <Text strong>{t('tasks.finishedAt')}:</Text>
                    <Text>{formatTime(selectedTask.finished_at)}</Text>
                  </Space>
                </Col>
              </Row>
            </Card>

            {selectedTask.execution_plan && (
              <Card size="small" className="nuwa-glass-card" title={t('tasks.executionPlan')}>
                <Row gutter={[16, 8]}>
                  <Col span={24}>
                    <Text strong>{t('tasks.analysis')}:</Text>
                    <div style={{ margin: '8px 0' }}>
                      {selectedTask.execution_plan.analysis}
                    </div>
                  </Col>
                  
                  {selectedTask.execution_plan.selected_functions && (
                    <Col span={24}>
                      <Text strong>{t('tasks.selectedFunctions')}:</Text>
                      <div style={{ marginTop: 8 }}>
                        {selectedTask.execution_plan.selected_functions.map((func, index) => (
                          <Tag key={index} style={{ marginRight: 8, marginBottom: 8 }}>
                            {func.plugin_name}.{func.function_name}
                          </Tag>
                        ))}
                      </div>
                    </Col>
                  )}
                </Row>
              </Card>
            )}
          </div>
        )}
      </Drawer>
      </div>
    </div>
  );
};

export default Tasks;