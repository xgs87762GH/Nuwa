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
  Modal,
  Form,
  Descriptions,
  Drawer,
  Badge,
  Tooltip,
  Empty,
  Statistic
} from 'antd';
import {
  ReloadOutlined,
  SearchOutlined,
  PlusOutlined,
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
import { createTask } from '../api/tasks';
import {
  TASK_STATUS,
  TASK_STATUS_LABELS,
  TASK_STATUS_COLORS
} from '../utils/constants';
import './Tasks.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [filters, setFilters] = useState({
    status: null,
    task_id: '',
    user_id: ''
  });
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [taskDetailVisible, setTaskDetailVisible] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [createForm] = Form.useForm();
  const refreshTimerRef = useRef(null);

  // Mock task data - moved to useMemo to fix ESLint warning
  const mockTasks = useMemo(() => [
    {
      task_id: "392e09da-ffbc-41f5-b0ff-6344543740e5",
      user_id: "1",
      description: "拍摄一张照片",
      created_at: "2025-09-22T02:27:50.891770",
      scheduled_at: "2025-09-22T02:27:50.891770",
      started_at: null,
      finished_at: null,
      status: "pending",
      priority: 1,
      timeout: 300,
      execution_plan: {
        analysis: "根据用户需求拍照，选择拍摄单张照片功能。",
        selected_functions: [
          {
            plugin_name: "Camera & Vision",
            function_name: "take_photo"
          }
        ]
      }
    },
    {
      task_id: "fadf1c88-07ec-470f-9f54-e8375b23e58c",
      user_id: "1",
      description: "拍摄照片，文件名为zhangsan223",
      created_at: "2025-09-16T13:16:37.641928",
      scheduled_at: "2025-09-16T13:16:37.641928",
      started_at: "2025-09-16T13:16:40.000000",
      finished_at: null,
      status: "running",
      priority: 2,
      timeout: 300,
      execution_plan: {
        analysis: "根据用户需求拍摄单张照片并保存指定文件名。",
        selected_functions: [
          {
            plugin_name: "Camera & Vision",
            function_name: "take_photo"
          }
        ]
      }
    },
    {
      task_id: "68e415e8-1b44-4ab3-babb-4d509d7031e9",
      user_id: "1",
      description: "录制一段视频",
      created_at: "2025-09-16T12:07:20.458935",
      scheduled_at: "2025-09-16T12:07:20.458935",
      started_at: "2025-09-16T12:07:25.000000",
      finished_at: "2025-09-16T12:08:30.000000",
      status: "success",
      priority: 0,
      timeout: 600,
      execution_plan: {
        analysis: "根据用户需求，需要对视频进行处理，可以选择'录制视频'功能来实现。",
        selected_functions: [
          {
            plugin_name: "Camera & Vision",
            function_name: "record_video"
          }
        ]
      }
    }
  ], []); // Empty dependency array since this is static mock data

  // Load task list
  const loadTasks = useCallback(async (page = pagination.current, pageSize = pagination.pageSize, currentFilters = filters) => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: pageSize,
        ...currentFilters
      };
      
      // 过滤空值
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      // 使用模拟数据
      const filteredTasks = mockTasks.filter(task => {
        if (currentFilters.status && task.status !== currentFilters.status) return false;
        if (currentFilters.task_id && !task.task_id.includes(currentFilters.task_id)) return false;
        if (currentFilters.user_id && !task.user_id.includes(currentFilters.user_id)) return false;
        return true;
      });

      setTasks(filteredTasks);
      setPagination({
        current: page,
        pageSize,
        total: filteredTasks.length
      });
    } catch (error) {
      console.error('Load tasks error:', error);
      message.error('加载任务列表失败');
    } finally {
      setLoading(false);
    }
  }, [filters, mockTasks, pagination]); // 添加缺失的依赖项

  // 清理轮询定时器
  const clearRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearInterval(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
  }, []);

  // 自动刷新逻辑
  useEffect(() => {
    clearRefreshTimer();
    if (autoRefresh) {
      refreshTimerRef.current = setInterval(() => {
        loadTasks();
      }, 5000);
    }
    return clearRefreshTimer;
  }, [autoRefresh, loadTasks, clearRefreshTimer]);

  // 手动刷新
  const handleRefresh = () => {
    loadTasks();
  };

  // 分页变化
  const handleTableChange = (paginationInfo) => {
    setPagination(prev => ({
      ...prev,
      current: paginationInfo.current,
      pageSize: paginationInfo.pageSize
    }));
    loadTasks(paginationInfo.current, paginationInfo.pageSize);
  };

  // 过滤条件变化
  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, current: 1 }));
    loadTasks(1, pagination.pageSize, newFilters);
  };

  // 自动刷新开关
  const handleAutoRefreshToggle = (checked) => {
    setAutoRefresh(checked);
  };

  // 创建任务
  const handleCreateTask = async (values) => {
    setCreateLoading(true);
    try {
      const response = await createTask(values.user_input);
      if (response.data?.success) {
        message.success('任务创建成功');
        setCreateModalVisible(false);
        createForm.resetFields();
        loadTasks(); // 重新加载任务列表
      } else {
        message.error(response.data?.message || '创建任务失败');
      }
    } catch (error) {
      console.error('Create task error:', error);
      message.error('网络错误，请稍后重试');
    } finally {
      setCreateLoading(false);
    }
  };

  // 查看任务详情
  const handleViewTask = (task) => {
    setSelectedTask(task);
    setTaskDetailVisible(true);
  };

  // 统计数据计算
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

  // 渲染统计卡片
  const renderStatsCards = () => (
    <Row gutter={[16, 16]} className="stats-cards">
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title="总任务"
            value={taskStats.total}
            prefix={<TeamOutlined className="stat-icon total" />}
            valueStyle={{ color: '#3f8bff', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title="运行中"
            value={taskStats.running}
            prefix={<FireOutlined className="stat-icon running" />}
            valueStyle={{ color: '#ff9500', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title="已完成"
            value={taskStats.completed}
            prefix={<TrophyOutlined className="stat-icon completed" />}
            valueStyle={{ color: '#52c41a', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card className="nuwa-glass-card" size="small">
          <Statistic
            title="失败/等待"
            value={taskStats.failed + taskStats.waiting}
            prefix={<BugOutlined className="stat-icon failed" />}
            valueStyle={{ color: '#ff4d4f', fontSize: '20px', fontWeight: 'bold' }}
          />
        </Card>
      </Col>
    </Row>
  );

  // 格式化时间
  const formatTime = (timeString) => {
    if (!timeString) return '-';
    try {
      const date = new Date(timeString);
      if (isNaN(date.getTime())) return '-';
      return date.toLocaleString('zh-CN');
    } catch (error) {
      return '-';
    }
  };

  // 获取状态图标
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

  // 获取优先级标签
  const getPriorityTag = (priority) => {
    const colors = ['default', 'blue', 'orange', 'red'];
    const labels = ['普通', '低', '中', '高'];
    return (
      <Tag color={colors[priority] || 'default'}>
        {labels[priority] || '普通'}
      </Tag>
    );
  };

  // 表格列定义
  const columns = [
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      width: 150,
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <Text code style={{ fontSize: '12px' }}>
            {text.substring(0, 8)}...
          </Text>
        </Tooltip>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Tag 
          color={TASK_STATUS_COLORS[status] || 'default'}
          icon={getStatusIcon(status)}
        >
          {TASK_STATUS_LABELS[status] || status}
        </Tag>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <Text>{text || '-'}</Text>
        </Tooltip>
      )
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority) => getPriorityTag(priority)
    },
    {
      title: '用户ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 100,
      render: (text) => (
        <Text code style={{ fontSize: '12px' }}>
          {text}
        </Text>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (text) => formatTime(text)
    },
    {
      title: '开始时间',
      dataIndex: 'started_at',
      key: 'started_at',
      width: 160,
      render: (text) => formatTime(text)
    },
    {
      title: '完成时间',
      dataIndex: 'finished_at',
      key: 'finished_at',
      width: 160,
      render: (text) => formatTime(text)
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewTask(record)}
            />
          </Tooltip>
          {record.status === 'pending' && (
            <Tooltip title="开始执行">
              <Button
                type="text"
                size="small"
                icon={<PlayCircleOutlined />}
                style={{ color: '#52c41a' }}
              />
            </Tooltip>
          )}
          {record.status === 'running' && (
            <Tooltip title="暂停">
              <Button
                type="text"
                size="small"
                icon={<PauseCircleOutlined />}
                style={{ color: '#faad14' }}
              />
            </Tooltip>
          )}
          <Tooltip title="删除">
            <Button
              type="text"
              size="small"
              icon={<DeleteOutlined />}
              danger
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
        <div className="tasks-header">
          <Title level={2} style={{ color: 'white', textAlign: 'center' }}>
            <Space>
              <SettingOutlined />
              任务管理
              <Badge count={tasks.length} showZero style={{ backgroundColor: '#52c41a' }} />
            </Space>
          </Title>
        </div>

        {/* 统计卡片 */}
        <div style={{ marginBottom: 16 }}>
          {renderStatsCards()}
        </div>

        {/* 筛选和操作区域 */}
        <Card className="nuwa-glass-card" style={{ marginBottom: 16 }}>
          <Row gutter={[16, 16]} align="middle">
            <Col xl={4} lg={6} md={8} sm={12} xs={24}>
              <Space>
                <Text strong style={{ color: 'var(--text-primary)' }}>状态:</Text>
                <Select
                  placeholder="选择状态"
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
                          {TASK_STATUS_LABELS[value]}
                        </Tag>
                      </Space>
                    </Option>
                  ))}
                </Select>
              </Space>
            </Col>          <Col xl={4} lg={6} md={8} sm={12} xs={24}>
            <Space>
              <Text strong>任务ID:</Text>
              <Input
                placeholder="输入任务ID"
                style={{ width: 140 }}
                value={filters.task_id}
                onChange={(e) => handleFiltersChange({ ...filters, task_id: e.target.value })}
                prefix={<SearchOutlined />}
              />
            </Space>
          </Col>

          <Col xl={4} lg={6} md={8} sm={12} xs={24}>
            <Space>
              <Text strong>用户ID:</Text>
              <Input
                placeholder="输入用户ID"
                style={{ width: 140 }}
                value={filters.user_id}
                onChange={(e) => handleFiltersChange({ ...filters, user_id: e.target.value })}
                prefix={<SearchOutlined />}
              />
            </Space>
          </Col>

          <Col xl={12} lg={6} md={24} sm={24} xs={24}>
            <Space wrap>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                创建任务
              </Button>

              <Button
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
                loading={loading}
              >
                刷新
              </Button>

              <Space>
                <Text>自动刷新:</Text>
                <Switch
                  checked={autoRefresh}
                  onChange={handleAutoRefreshToggle}
                  checkedChildren={<SyncOutlined />}
                  unCheckedChildren="关"
                />
              </Space>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 任务列表 */}
      <Card className="nuwa-glass-card">
        <div style={{ 
          background: 'transparent',
          '& .ant-table': { background: 'transparent' },
          '& .ant-table-thead > tr > th': {
            background: 'rgba(255, 255, 255, 0.1)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
            color: 'white'
          },
          '& .ant-table-tbody > tr': { background: 'transparent' },
          '& .ant-table-tbody > tr:hover': { background: 'rgba(255, 255, 255, 0.05)' },
          '& .ant-table-tbody > tr > td': {
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            color: 'rgba(255, 255, 255, 0.9)'
          }
        }}>
          <Table
            columns={columns}
            dataSource={tasks}
            loading={loading}
            pagination={{
              ...pagination,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) =>
                `第 ${range[0]}-${range[1]} 条 / 共 ${total} 条`,
              pageSizeOptions: ['10', '20', '50', '100'],
              size: 'small'
            }}
            onChange={handleTableChange}
            rowKey="task_id"
            scroll={{ x: 1200 }}
            size="middle"
            locale={{
              emptyText: (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description="暂无任务数据"
                />
              )
            }}
          />
        </div>
      </Card>

      {/* 创建任务弹窗 */}
      <Modal
        title="创建新任务"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          createForm.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={handleCreateTask}
        >
          <Form.Item
            name="user_input"
            label="任务描述"
            rules={[
              { required: true, message: '请输入任务描述' },
              { min: 5, message: '任务描述至少5个字符' }
            ]}
          >
            <TextArea
              rows={4}
              placeholder="请详细描述您要执行的任务，例如：拍摄一张照片、录制30秒视频等..."
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => {
                setCreateModalVisible(false);
                createForm.resetFields();
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={createLoading}>
                创建任务
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 任务详情抽屉 */}
      <Drawer
        title="任务详情"
        open={taskDetailVisible}
        onClose={() => setTaskDetailVisible(false)}
        width={600}
      >
        {selectedTask && (
          <div>
            <Descriptions title="基本信息" bordered size="small">
              <Descriptions.Item label="任务ID" span={3}>
                <Text code>{selectedTask.task_id}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag 
                  color={TASK_STATUS_COLORS[selectedTask.status]}
                  icon={getStatusIcon(selectedTask.status)}
                >
                  {TASK_STATUS_LABELS[selectedTask.status]}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="优先级">
                {getPriorityTag(selectedTask.priority)}
              </Descriptions.Item>
              <Descriptions.Item label="用户ID">
                <Text code>{selectedTask.user_id}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={3}>
                {selectedTask.description}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {formatTime(selectedTask.created_at)}
              </Descriptions.Item>
              <Descriptions.Item label="开始时间">
                {formatTime(selectedTask.started_at)}
              </Descriptions.Item>
              <Descriptions.Item label="完成时间">
                {formatTime(selectedTask.finished_at)}
              </Descriptions.Item>
              <Descriptions.Item label="超时时间">
                {selectedTask.timeout ? `${selectedTask.timeout}秒` : '-'}
              </Descriptions.Item>
            </Descriptions>

            {selectedTask.execution_plan && (
              <div style={{ marginTop: 24 }}>
                <Title level={4}>执行计划</Title>
                <Card size="small">
                  <Descriptions size="small">
                    <Descriptions.Item label="分析" span={3}>
                      {selectedTask.execution_plan.analysis}
                    </Descriptions.Item>
                  </Descriptions>
                  
                  {selectedTask.execution_plan.selected_functions && (
                    <div style={{ marginTop: 16 }}>
                      <Text strong>选择的功能:</Text>
                      {selectedTask.execution_plan.selected_functions.map((func, index) => (
                        <Tag key={index} style={{ marginTop: 8, display: 'block' }}>
                          {func.plugin_name}.{func.function_name}
                        </Tag>
                      ))}
                    </div>
                  )}
                </Card>
              </div>
            )}
          </div>
        )}
      </Drawer>
      </div>
    </div>
  );
};

export default Tasks;