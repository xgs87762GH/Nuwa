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
  Statistic,
  Modal,
  Tabs
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
  BugOutlined,
  InfoCircleOutlined,
  ApiOutlined
} from '@ant-design/icons';
import { getTasksList,deleteTask,getTaskDetails } from '../api/tasks';
import {
  TASK_STATUS,
  TASK_STATUS_LABELS,
  TASK_STATUS_COLORS
} from '../utils/constants';
import TaskStepsVisualization from '../components/TaskStepsVisualization';
import '../styles/Tasks.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

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
  const [taskDetailLoading, setTaskDetailLoading] = useState(false);
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
      }, 10000);
    }
    return clearRefreshTimer;
  }, [autoRefresh, loadTasks, clearRefreshTimer]);

  // Manual refresh
  const handleRefresh = () => {
    loadTasks();
  };

  // Delete task
  const handleDeleteTask = async (taskId) => {
    try {
      const response = await deleteTask(taskId);
      if (response?.success) {
        message.success(t('tasks.deleteTaskSuccess'));
        // Refresh the task list after successful deletion
        loadTasks();
      } else {
        message.error(response?.message || t('tasks.deleteTaskFailed'));
      }
    } catch (error) {
      console.error('Delete task error:', error);
      message.error(t('tasks.deleteTaskFailed'));
    }
  };

  // Confirm delete task
  const handleConfirmDelete = (task) => {
    // Use Ant Design's Modal.confirm for better UX
    Modal.confirm({
      title: t('tasks.confirmDelete'),
      content: (
        <div>
          <p>{t('tasks.deleteTaskContent')}</p>
          <p><strong>{t('tasks.taskId')}:</strong> {task.task_id}</p>
          <p><strong>{t('tasks.taskDescription')}:</strong> {task.description}</p>
        </div>
      ),
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      okType: 'danger',
      onOk: () => handleDeleteTask(task.task_id),
      onCancel: () => {
        console.log('Delete cancelled');
      },
    });
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

  // Load detailed task information
  const loadTaskDetails = async (taskId) => {
    setTaskDetailLoading(true);
    try {
      const response = await getTaskDetails(taskId);
      if (response?.success) {
        return response.data;
      } else {
        message.error(response?.message || t('tasks.loadTaskDetailsFailed'));
        return null;
      }
    } catch (error) {
      console.error('Load task details error:', error);
      message.error(t('tasks.loadTaskDetailsFailed'));
      return null;
    } finally {
      setTaskDetailLoading(false);
    }
  };

  // View task details
  const handleViewTask = async (task) => {
    // First set the basic task info and show the drawer
    setSelectedTask(task);
    setTaskDetailVisible(true);
    
    // Then load detailed information with API call
    const detailedTask = await loadTaskDetails(task.task_id);
    if (detailedTask) {
      // Update with detailed information
      setSelectedTask(detailedTask);
    }
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
            valueStyle={{ color: 'var(--color-info)', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title={t('tasks.activeTasks')}
            value={taskStats.running}
            prefix={<FireOutlined className="stat-icon running" />}
            valueStyle={{ color: 'var(--color-warning)', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title={t('tasks.completedTasks')}
            value={taskStats.completed}
            prefix={<TrophyOutlined className="stat-icon completed" />}
            valueStyle={{ color: 'var(--color-success)', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title={t('tasks.failedTasks')}
            value={taskStats.failed + taskStats.waiting}
            prefix={<BugOutlined className="stat-icon failed" />}
            valueStyle={{ color: 'var(--color-error)', fontSize: '20px', fontWeight: 'bold' }}
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
        return <ClockCircleOutlined style={{ color: 'var(--color-warning)' }} />;
      case 'running':
        return <SyncOutlined spin style={{ color: 'var(--color-info)' }} />;
      case 'success':
      case 'completed':
        return <CheckCircleOutlined style={{ color: 'var(--color-success)' }} />;
      case 'failed':
        return <ExclamationCircleOutlined style={{ color: 'var(--color-error)' }} />;
      default:
        return <ClockCircleOutlined style={{ color: 'var(--text-muted)' }} />;
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
              background: 'var(--glass-bg)',
              padding: '2px 6px',
              borderRadius: '4px',
              color: 'var(--color-info)'
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
        <Text style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
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
        <Text style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
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
        <Text style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
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
              className="action-btn view-btn"
            />
          </Tooltip>
          {record.status === 'pending' && (
            <Tooltip title={t('tasks.actions.start')}>
              <Button
                type="text"
                size="small"
                icon={<PlayCircleOutlined />}
                className="action-btn start-btn"
              />
            </Tooltip>
          )}
          {record.status === 'running' && (
            <Tooltip title={t('tasks.actions.pause')}>
              <Button
                type="text"
                size="small"
                icon={<PauseCircleOutlined />}
                className="action-btn pause-btn"
              />
            </Tooltip>
          )}
          <Tooltip title={t('tasks.actions.delete')}>
            <Button
              type="text"
              size="small"
              icon={<DeleteOutlined />}
              onClick={() => handleConfirmDelete(record)}
              className="action-btn delete-btn"
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
                  className="nuwa-input"
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
                  className="nuwa-input"
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
                    <span style={{ color: 'var(--text-muted)' }}>
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
        title={
          <Space>
            <InfoCircleOutlined />
            {t('tasks.taskDetails')}
            {selectedTask && (
              <Tag color={TASK_STATUS_COLORS[selectedTask.status]} style={{ marginLeft: 8 }}>
                {t(TASK_STATUS_LABELS[selectedTask.status])}
              </Tag>
            )}
            {taskDetailLoading && (
              <SyncOutlined spin style={{ marginLeft: 8, color: 'var(--color-info)' }} />
            )}
          </Space>
        }
        open={taskDetailVisible}
        onClose={() => {
          setTaskDetailVisible(false);
          setSelectedTask(null);
          setTaskDetailLoading(false);
        }}
        width={800}
        bodyStyle={{ padding: 0 }}
        className="nuwa-drawer"
        headerStyle={{ 
          borderBottom: '1px solid var(--border-color, rgba(255, 255, 255, 0.1))'
        }}
      >
        {selectedTask && (
          <Tabs defaultActiveKey="overview" style={{ height: '100%' }}>
            <TabPane 
              tab={
                <Space>
                  <InfoCircleOutlined />
                  {t('tasks.overview')}
                </Space>
              } 
              key="overview"
            >
              <div style={{ padding: 16 }}>
                {/* Basic Information */}
                <Card size="small" className="nuwa-glass-card" style={{ marginBottom: 16 }}>
                  <Row gutter={[16, 12]}>
                    <Col span={24}>
                      <Space>
                        <Text strong>{t('tasks.taskId')}:</Text>
                        <Text 
                          code 
                          copyable={{ text: selectedTask.task_id }}
                          style={{ 
                            fontSize: '12px',
                            background: 'var(--glass-bg)',
                            color: 'var(--color-info)',
                            padding: '2px 6px',
                            borderRadius: '4px'
                          }}
                        >
                          {selectedTask.task_id}
                        </Text>
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
                      <div style={{ 
                        margin: '8px 0',
                        padding: '8px 12px',
                        background: 'var(--glass-bg)',
                        borderRadius: '6px',
                        border: '1px solid var(--glass-border)'
                      }}>
                        {selectedTask.description}
                      </div>
                    </Col>
                    <Col span={8}>
                      <Text strong>{t('tasks.createdAt')}:</Text>
                      <br />
                      <Text style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {formatTime(selectedTask.created_at)}
                      </Text>
                    </Col>
                    <Col span={8}>
                      <Text strong>{t('tasks.startedAt')}:</Text>
                      <br />
                      <Text style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {formatTime(selectedTask.started_at)}
                      </Text>
                    </Col>
                    <Col span={8}>
                      <Text strong>{t('tasks.finishedAt')}:</Text>
                      <br />
                      <Text style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {formatTime(selectedTask.finished_at)}
                      </Text>
                    </Col>
                  </Row>
                </Card>

                {/* Task Result or Error */}
                {selectedTask.result && (
                  <Card size="small" className="nuwa-glass-card" style={{ marginBottom: 16 }}>
                    <Row gutter={[16, 8]}>
                      <Col span={24}>
                        <Text strong>{t('tasks.taskResult')}:</Text>
                        <div style={{ 
                          marginTop: 8,
                          padding: '12px',
                          background: 'rgba(82, 196, 26, 0.1)',
                          border: '1px solid rgba(82, 196, 26, 0.3)',
                          borderRadius: '6px',
                          fontFamily: 'Monaco, Consolas, monospace',
                          fontSize: '12px',
                          whiteSpace: 'pre-wrap',
                          maxHeight: '300px',
                          overflow: 'auto'
                        }}>
                          {typeof selectedTask.result === 'object' 
                            ? JSON.stringify(selectedTask.result, null, 2)
                            : String(selectedTask.result)
                          }
                        </div>
                      </Col>
                    </Row>
                  </Card>
                )}

                {selectedTask.error && (
                  <Card size="small" className="nuwa-glass-card" style={{ marginBottom: 16 }}>
                    <Row gutter={[16, 8]}>
                      <Col span={24}>
                        <Text strong style={{ color: '#ff4d4f' }}>{t('tasks.taskError')}:</Text>
                        <div style={{ 
                          marginTop: 8,
                          padding: '12px',
                          background: 'rgba(255, 77, 79, 0.1)',
                          border: '1px solid rgba(255, 77, 79, 0.3)',
                          borderRadius: '6px',
                          fontFamily: 'Monaco, Consolas, monospace',
                          fontSize: '12px',
                          whiteSpace: 'pre-wrap'
                        }}>
                          {selectedTask.error}
                        </div>
                      </Col>
                    </Row>
                  </Card>
                )}
              </div>
            </TabPane>

            <TabPane 
              tab={
                <Space>
                  <ApiOutlined />
                  {t('tasks.executionDetails')}
                </Space>
              } 
              key="execution"
            >
              <div style={{ padding: 16 }}>
                <TaskStepsVisualization task={selectedTask} />
              </div>
            </TabPane>

            {selectedTask.extra && (
              <TabPane 
                tab={
                  <Space>
                    <SettingOutlined />
                    {t('tasks.additionalInfo')}
                  </Space>
                } 
                key="extra"
              >
                <div style={{ padding: 16 }}>
                  <Card size="small" className="nuwa-glass-card">
                    <pre style={{ 
                      fontSize: '12px',
                      fontFamily: 'Monaco, Consolas, monospace',
                      background: 'transparent',
                      border: 'none',
                      margin: 0,
                      whiteSpace: 'pre-wrap',
                      color: 'var(--text-secondary)'
                    }}>
                      {JSON.stringify(selectedTask.extra, null, 2)}
                    </pre>
                  </Card>
                </div>
              </TabPane>
            )}
          </Tabs>
        )}
      </Drawer>
      </div>
    </div>
  );
};

export default Tasks;