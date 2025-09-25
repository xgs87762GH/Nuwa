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

  // Format step result for better display - more generic approach
  const formatStepResult = (step) => {
    if (!step.result) return null;
    
    const result = step.result;
    
    // Try to extract key information from result object
    if (typeof result === 'object' && result !== null) {
      const keyFields = [];
      
      // Common fields that might be interesting to highlight
      if (result.status) keyFields.push(`📊 Status: ${result.status}`);
      if (result.file_path) keyFields.push(`📁 File: ${result.file_path}`);
      if (result.filename) keyFields.push(`📄 Name: ${result.filename}`);
      if (result.file_size) {
        const size = result.file_size;
        const formatted = size > 1024 * 1024 
          ? `${(size / 1024 / 1024).toFixed(1)}MB`
          : `${(size / 1024).toFixed(1)}KB`;
        keyFields.push(`📦 Size: ${formatted}`);
      }
      if (result.duration) keyFields.push(`⏱️ Duration: ${result.duration.toFixed ? result.duration.toFixed(1) : result.duration}s`);
      if (result.resolution) keyFields.push(`📏 Resolution: ${result.resolution[0]}×${result.resolution[1]}`);
      
      // If we found key fields, show them in a nice format, otherwise show JSON
      if (keyFields.length > 0) {
        return (
          <div style={{ lineHeight: '1.5' }}>
            <div style={{ marginBottom: '8px', fontWeight: 'bold', color: 'var(--text-primary, #fff)' }}>
              {t('tasks.keyInfo')}:
            </div>
            {keyFields.map((field, index) => (
              <div key={index} style={{ 
                marginBottom: '4px', 
                fontSize: '12px',
                color: 'var(--text-secondary, rgba(255, 255, 255, 0.8))'
              }}>
                {field}
              </div>
            ))}
            <details style={{ marginTop: '8px' }}>
              <summary style={{ 
                cursor: 'pointer', 
                fontSize: '11px',
                color: 'var(--text-tertiary, rgba(255, 255, 255, 0.6))'
              }}>
                {t('tasks.showFullResult')}
              </summary>
              <pre style={{
                marginTop: '8px',
                fontSize: '10px',
                fontFamily: 'Monaco, Consolas, monospace',
                whiteSpace: 'pre-wrap',
                background: 'rgba(0, 0, 0, 0.2)',
                padding: '8px',
                borderRadius: '4px',
                color: 'var(--text-secondary, rgba(255, 255, 255, 0.8))',
                maxHeight: '150px',
                overflow: 'auto'
              }}>
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </div>
        );
      }
    }
    
    // Fallback to JSON display for non-object or unrecognized results
    return (
      <pre style={{
        fontSize: '11px',
        fontFamily: 'Monaco, Consolas, monospace',
        whiteSpace: 'pre-wrap',
        background: 'rgba(0, 0, 0, 0.2)',
        padding: '8px',
        borderRadius: '4px',
        color: 'var(--text-secondary, rgba(255, 255, 255, 0.8))',
        maxHeight: '150px',
        overflow: 'auto',
        margin: 0
      }}>
        {typeof result === 'object' 
          ? JSON.stringify(result, null, 2)
          : String(result)
        }
      </pre>
    );
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
                    background: 'var(--card-bg, rgba(255, 255, 255, 0.03))',
                    border: `1px solid var(--border-color, rgba(255, 255, 255, 0.1))`,
                    borderRadius: '8px',
                    backdropFilter: 'blur(8px)',
                    ...(step.status === 'running' && {
                      borderColor: 'var(--primary-color, #1890ff)',
                      boxShadow: '0 0 8px rgba(24, 144, 255, 0.3)'
                    }),
                    ...(step.status === 'success' && {
                      borderColor: 'var(--success-color, #52c41a)',
                      boxShadow: '0 0 8px rgba(82, 196, 26, 0.2)'
                    }),
                    ...(step.status === 'failed' && {
                      borderColor: 'var(--error-color, #ff4d4f)',
                      boxShadow: '0 0 8px rgba(255, 77, 79, 0.2)'
                    })
                  }}
                >
                  <Row gutter={[16, 8]}>
                    <Col span={24}>
                      <Space wrap>
                        <Text 
                          strong 
                          style={{ 
                            color: 'var(--text-primary, #fff)',
                            fontSize: '13px' 
                          }}
                        >
                          {t('tasks.step')} {index + 1}:
                        </Text>
                        <Tag 
                          color="blue" 
                          style={{ 
                            background: 'rgba(24, 144, 255, 0.15)',
                            borderColor: 'rgba(24, 144, 255, 0.4)',
                            color: 'var(--primary-color, #40a9ff)'
                          }}
                        >
                          {step.plugin_name}
                        </Tag>
                        <Tag style={{
                          background: 'rgba(255, 255, 255, 0.1)',
                          borderColor: 'rgba(255, 255, 255, 0.2)',
                          color: 'var(--text-secondary, rgba(255, 255, 255, 0.8))'
                        }}>
                          {step.function_name}
                        </Tag>
                        <Tag 
                          color={TASK_STATUS_COLORS[step.status]}
                          style={{
                            fontWeight: 'bold'
                          }}
                        >
                          {t(`tasks.status.${step.status}`)}
                        </Tag>
                      </Space>
                    </Col>
                    
                    {/* Step Parameters */}
                    {step.params && Object.keys(step.params).length > 0 && (
                      <Col span={24}>
                        <Text 
                          strong 
                          style={{ 
                            color: 'var(--text-primary, #fff)',
                            fontSize: '12px' 
                          }}
                        >
                          {t('tasks.stepParams')}:
                        </Text>
                        <div style={{ marginTop: 6 }}>
                          {Object.entries(step.params).map(([key, value]) => (
                            <Tag 
                              key={key} 
                              style={{ 
                                margin: '2px 4px 4px 0',
                                background: 'rgba(255, 255, 255, 0.08)',
                                borderColor: 'rgba(255, 255, 255, 0.15)',
                                color: 'var(--text-secondary, rgba(255, 255, 255, 0.8))',
                                fontSize: '11px'
                              }}
                            >
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
                          <Text 
                            type="secondary" 
                            style={{ 
                              fontSize: '12px',
                              color: 'var(--text-tertiary, rgba(255, 255, 255, 0.6))',
                              display: 'block'
                            }}
                          >
                            {t('tasks.startedAt')}: 
                          </Text>
                          <Text style={{ 
                            fontSize: '11px',
                            color: 'var(--text-secondary, rgba(255, 255, 255, 0.8))'
                          }}>
                            {formatTime(step.started_at)}
                          </Text>
                        </Col>
                        <Col span={8}>
                          <Text 
                            type="secondary" 
                            style={{ 
                              fontSize: '12px',
                              color: 'var(--text-tertiary, rgba(255, 255, 255, 0.6))',
                              display: 'block'
                            }}
                          >
                            {t('tasks.finishedAt')}:
                          </Text>
                          <Text style={{ 
                            fontSize: '11px',
                            color: 'var(--text-secondary, rgba(255, 255, 255, 0.8))'
                          }}>
                            {formatTime(step.finished_at)}
                          </Text>
                        </Col>
                        <Col span={8}>
                          <Text 
                            type="secondary" 
                            style={{ 
                              fontSize: '12px',
                              color: 'var(--text-tertiary, rgba(255, 255, 255, 0.6))',
                              display: 'block'
                            }}
                          >
                            {t('tasks.duration')}:
                          </Text>
                          <Text style={{ 
                            fontSize: '11px',
                            color: 'var(--text-secondary, rgba(255, 255, 255, 0.8))'
                          }}>
                            {formatDuration(step.started_at, step.finished_at)}
                          </Text>
                        </Col>
                      </Row>
                    </Col>

                    {/* Retry Information */}
                    {step.retry_count > 0 && (
                      <Col span={24}>
                        <Alert
                          message={
                            <Text 
                              strong
                              style={{ 
                                color: 'var(--warning-color, #faad14)',
                                fontSize: '12px'
                              }}
                            >
                              {t('tasks.retryInfo', { 
                                current: step.retry_count, 
                                max: step.max_retries 
                              })}
                            </Text>
                          }
                          type="warning"
                          size="small"
                          showIcon
                          style={{
                            background: 'var(--warning-bg, rgba(250, 173, 20, 0.08))',
                            border: '1px solid var(--warning-border, rgba(250, 173, 20, 0.3))',
                            borderRadius: '6px'
                          }}
                        />
                      </Col>
                    )}

                    {/* Error Information */}
                    {step.error && (
                      <Col span={24}>
                        <Alert
                          message={
                            <Text 
                              strong
                              style={{ 
                                color: 'var(--error-color, #ff4d4f)',
                                fontSize: '12px'
                              }}
                            >
                              {t('tasks.stepError')}
                            </Text>
                          }
                          description={
                            <div style={{
                              fontSize: '11px',
                              fontFamily: 'Monaco, Consolas, monospace',
                              whiteSpace: 'pre-wrap',
                              color: 'var(--error-color, #ff4d4f)',
                              opacity: 0.8
                            }}>
                              {step.error}
                            </div>
                          }
                          type="error"
                          size="small"
                          showIcon
                          style={{
                            background: 'var(--error-bg, rgba(255, 77, 79, 0.08))',
                            border: '1px solid var(--error-border, rgba(255, 77, 79, 0.3))',
                            borderRadius: '6px'
                          }}
                        />
                      </Col>
                    )}

                    {/* Result Information */}
                    {step.result && (
                      <Col span={24}>
                        <Alert
                          message={
                            <Text 
                              strong
                              style={{ 
                                color: 'var(--success-color, #52c41a)',
                                fontSize: '12px'
                              }}
                            >
                              {t('tasks.stepResult')}
                            </Text>
                          }
                          description={
                            <div style={{ 
                              maxHeight: '200px', 
                              overflow: 'auto',
                              paddingRight: '4px'
                            }}>
                              {formatStepResult(step)}
                            </div>
                          }
                          type="success"
                          size="small"
                          showIcon
                          style={{
                            background: 'var(--success-bg, rgba(82, 196, 26, 0.08))',
                            border: '1px solid var(--success-border, rgba(82, 196, 26, 0.3))',
                            borderRadius: '6px'
                          }}
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