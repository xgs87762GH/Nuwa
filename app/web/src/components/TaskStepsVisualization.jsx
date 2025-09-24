import React from 'react';
import {
  Card,
  Steps,
  Tag,
  Typography,
  Row,
  Col,
  Progress,
  Descriptions,
  Alert,
  Space,
  Divider,
  Timeline
} from 'antd';
import {
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SyncOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  BugOutlined,
  ApiOutlined,
  FunctionOutlined
} from '@ant-design/icons';
import { useLanguage } from '../contexts/LanguageContext';
import { TASK_STATUS_COLORS } from '../utils/constants';

const { Text, Title } = Typography;
const { Step } = Steps;

const TaskStepsVisualization = ({ task }) => {
  const { t } = useLanguage();

  if (!task) return null;

  // Get step status icon
  const getStepStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      case 'running':
        return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      case 'success':
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'cancelled':
        return <StopOutlined style={{ color: '#d9d9d9' }} />;
      case 'paused':
        return <PauseCircleOutlined style={{ color: '#faad14' }} />;
      case 'timeout':
        return <BugOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  // Get step status for Steps component
  const getStepStatus = (status) => {
    switch (status) {
      case 'success':
      case 'completed':
        return 'finish';
      case 'running':
        return 'process';
      case 'failed':
      case 'timeout':
        return 'error';
      case 'pending':
      case 'cancelled':
      case 'paused':
      default:
        return 'wait';
    }
  };

  // Calculate overall progress
  const calculateProgress = () => {
    if (!task.steps || task.steps.length === 0) return 0;
    
    const completedSteps = task.steps.filter(step => 
      step.status === 'success' || step.status === 'completed'
    ).length;
    
    return Math.round((completedSteps / task.steps.length) * 100);
  };

  // Get current step index
  const getCurrentStepIndex = () => {
    if (!task.steps || task.steps.length === 0) return 0;
    
    const runningIndex = task.steps.findIndex(step => step.status === 'running');
    if (runningIndex !== -1) return runningIndex;
    
    const lastCompletedIndex = task.steps
      .map((step, index) => ({ step, index }))
      .filter(({ step }) => step.status === 'success' || step.status === 'completed')
      .pop()?.index;
    
    return lastCompletedIndex !== undefined ? lastCompletedIndex + 1 : 0;
  };

  // Format time
  const formatTime = (timeString) => {
    if (!timeString) return '-';
    try {
      const date = new Date(timeString);
      if (isNaN(date.getTime())) return '-';
      const locale = t('common.locale') === 'zh' ? 'zh-CN' : 'en-US';
      return date.toLocaleString(locale);
    } catch (error) {
      return '-';
    }
  };

  // Format duration
  const formatDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return '-';
    try {
      const start = new Date(startTime);
      const end = new Date(endTime);
      const diff = end - start;
      
      if (diff < 1000) return `${diff}ms`;
      if (diff < 60000) return `${Math.round(diff / 1000)}s`;
      return `${Math.round(diff / 60000)}m`;
    } catch (error) {
      return '-';
    }
  };

  const progress = calculateProgress();
  const currentStep = getCurrentStepIndex();

  return (
    <div>
      {/* Overall Progress */}
      <Card size="small" className="nuwa-glass-card" style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>{t('tasks.executionProgress')}</Text>
              <Progress
                percent={progress}
                status={task.status === 'failed' ? 'exception' : task.status === 'running' ? 'active' : 'normal'}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
                size="small"
                showInfo={true}
                format={(percent) => `${percent}% (${task.steps?.filter(s => s.status === 'success' || s.status === 'completed').length || 0}/${task.steps?.length || 0})`}
              />
            </Space>
          </Col>
          <Col xs={24} sm={12}>
            <Space>
              <Text strong>{t('tasks.currentStep')}:</Text>
              <Tag color={TASK_STATUS_COLORS[task.status]} icon={getStepStatusIcon(task.status)}>
                {currentStep + 1} / {task.steps?.length || 0}
              </Tag>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Execution Plan */}
      {task.execution_plan && (
        <Card 
          size="small" 
          className="nuwa-glass-card" 
          title={
            <Space>
              <ApiOutlined />
              {t('tasks.executionPlan')}
            </Space>
          }
          style={{ marginBottom: 16 }}
        >
          <Descriptions column={1} size="small">
            <Descriptions.Item label={t('tasks.analysis')}>
              <Text>{task.execution_plan.analysis}</Text>
            </Descriptions.Item>
            <Descriptions.Item label={t('tasks.overallConfidence')}>
              <Progress 
                percent={Math.round((task.execution_plan.overall_confidence || 0) * 100)} 
                size="small"
                strokeColor="#52c41a"
                style={{ width: '200px' }}
              />
            </Descriptions.Item>
          </Descriptions>
          
          {task.execution_plan.selected_functions && task.execution_plan.selected_functions.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <Text strong>{t('tasks.selectedFunctions')}:</Text>
              <div style={{ marginTop: 8 }}>
                {task.execution_plan.selected_functions.map((func, index) => (
                  <Tag 
                    key={index} 
                    icon={<FunctionOutlined />}
                    color="blue"
                    style={{ margin: '4px 8px 4px 0' }}
                  >
                    {func.plugin_name}.{func.function_name}
                  </Tag>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Steps Visualization */}
      {task.steps && task.steps.length > 0 && (
        <Card 
          size="small" 
          className="nuwa-glass-card"
          title={
            <Space>
              <PlayCircleOutlined />
              {t('tasks.executionSteps')}
            </Space>
          }
        >
          {/* Steps Overview */}
          <Steps 
            current={currentStep} 
            size="small"
            style={{ marginBottom: 24 }}
          >
            {task.steps.map((step, index) => (
              <Step
                key={step.step_id}
                title={`${t('tasks.step')} ${index + 1}`}
                description={step.function_name}
                status={getStepStatus(step.status)}
                icon={getStepStatusIcon(step.status)}
              />
            ))}
          </Steps>

          <Divider />

          {/* Detailed Steps Timeline */}
          <Timeline mode="left" style={{ marginTop: 16 }}>
            {task.steps.map((step, index) => (
              <Timeline.Item
                key={step.step_id}
                dot={getStepStatusIcon(step.status)}
                color={TASK_STATUS_COLORS[step.status]}
              >
                <Card 
                  size="small" 
                  style={{ 
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: `1px solid ${TASK_STATUS_COLORS[step.status] === 'processing' ? '#1890ff' : 'rgba(255, 255, 255, 0.1)'}`
                  }}
                >
                  <Row gutter={[16, 8]}>
                    <Col span={24}>
                      <Space>
                        <Text strong>{t('tasks.step')} {index + 1}:</Text>
                        <Tag color="blue">{step.plugin_name}</Tag>
                        <Tag>{step.function_name}</Tag>
                        <Tag color={TASK_STATUS_COLORS[step.status]}>
                          {t(`tasks.status.${step.status}`)}
                        </Tag>
                      </Space>
                    </Col>
                    
                    {/* Step Parameters */}
                    {step.params && Object.keys(step.params).length > 0 && (
                      <Col span={24}>
                        <Text strong>{t('tasks.stepParams')}:</Text>
                        <div style={{ marginTop: 4 }}>
                          {Object.entries(step.params).map(([key, value]) => (
                            <Tag key={key} style={{ margin: '2px 4px 2px 0' }}>
                              {key}: {String(value)}
                            </Tag>
                          ))}
                        </div>
                      </Col>
                    )}

                    {/* Timing Information */}
                    <Col span={24}>
                      <Row gutter={16}>
                        <Col span={8}>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {t('tasks.startedAt')}: {formatTime(step.started_at)}
                          </Text>
                        </Col>
                        <Col span={8}>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {t('tasks.finishedAt')}: {formatTime(step.finished_at)}
                          </Text>
                        </Col>
                        <Col span={8}>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {t('tasks.duration')}: {formatDuration(step.started_at, step.finished_at)}
                          </Text>
                        </Col>
                      </Row>
                    </Col>

                    {/* Retry Information */}
                    {step.retry_count > 0 && (
                      <Col span={24}>
                        <Alert
                          message={t('tasks.retryInfo', { 
                            current: step.retry_count, 
                            max: step.max_retries 
                          })}
                          type="warning"
                          size="small"
                          showIcon
                        />
                      </Col>
                    )}

                    {/* Error Information */}
                    {step.error && (
                      <Col span={24}>
                        <Alert
                          message={t('tasks.stepError')}
                          description={step.error}
                          type="error"
                          size="small"
                          showIcon
                        />
                      </Col>
                    )}

                    {/* Result Information */}
                    {step.result && (
                      <Col span={24}>
                        <Alert
                          message={t('tasks.stepResult')}
                          description={
                            typeof step.result === 'object' 
                              ? JSON.stringify(step.result, null, 2)
                              : String(step.result)
                          }
                          type="success"
                          size="small"
                          showIcon
                        />
                      </Col>
                    )}
                  </Row>
                </Card>
              </Timeline.Item>
            ))}
          </Timeline>
        </Card>
      )}
    </div>
  );
};

export default TaskStepsVisualization;