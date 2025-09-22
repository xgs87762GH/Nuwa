import React, { useState, useEffect } from 'react';
import { 
  Select, 
  Card, 
  Row, 
  Col, 
  Tooltip, 
  Badge, 
  Typography, 
  Space,
  Slider,
  InputNumber,
  Switch,
  message,
  Spin
} from 'antd';
import { 
  RobotOutlined, 
  ThunderboltOutlined, 
  SettingOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import { getAIServices, getAIModels, getServiceStatus, setDefaultAIProvider, getCurrentAIProvider } from '../api/ai';

const { Option } = Select;
const { Text, Paragraph } = Typography;

const AIModelSelector = ({ 
  selectedService, 
  selectedModel, 
  onServiceChange, 
  onModelChange,
  onSettingsChange,
  settings = {}
}) => {
  const [services, setServices] = useState([]);
  const [models, setModels] = useState([]);
  const [serviceStatus, setServiceStatus] = useState({});
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [currentProvider, setCurrentProvider] = useState(null);

  // 默认设置
  const defaultSettings = {
    temperature: 0.7,
    maxTokens: 2048,
    stream: false,
    ...settings
  };

  const [currentSettings, setCurrentSettings] = useState(defaultSettings);

  // 加载AI服务列表
  useEffect(() => {
    loadServices();
    loadCurrentProvider();
  }, []);

  // 当服务改变时加载模型列表
  useEffect(() => {
    if (selectedService) {
      loadModels(selectedService);
      checkServiceStatus(selectedService);
    }
  }, [selectedService]);

  const loadServices = async () => {
    try {
      setLoading(true);
      const response = await getAIServices();
      const providers = response.data?.providers || [];
      
      // 转换为前端需要的格式
      const formattedServices = providers.map(provider => ({
        id: provider.type,
        name: provider.type.charAt(0).toUpperCase() + provider.type.slice(1),
        provider: provider.type,
        description: `${provider.type} AI服务`,
        status: provider.status,
        default_model: provider.default_model,
        models: provider.models || []
      }));
      
      setServices(formattedServices);
    } catch (error) {
      console.error('加载AI服务失败:', error);
      message.error('加载AI服务失败');
    } finally {
      setLoading(false);
    }
  };

  const loadCurrentProvider = async () => {
    try {
      const response = await getCurrentAIProvider();
      setCurrentProvider(response.data);
    } catch (error) {
      console.error('加载当前提供商失败:', error);
    }
  };

  const loadModels = async (providerType) => {
    try {
      setLoading(true);
      const response = await getAIModels(providerType);
      const modelList = response.data || [];
      
      // 转换为前端需要的格式
      const formattedModels = modelList.map(modelId => ({
        id: modelId,
        name: modelId,
        description: `${modelId} 模型`
      }));
      
      setModels(formattedModels);
    } catch (error) {
      console.error('加载AI模型失败:', error);
      message.error('加载AI模型失败');
    } finally {
      setLoading(false);
    }
  };

  const checkServiceStatus = async (providerType) => {
    try {
      const response = await getServiceStatus(providerType);
      setServiceStatus(prev => ({
        ...prev,
        [providerType]: response.data
      }));
    } catch (error) {
      console.error('检查服务状态失败:', error);
    }
  };

  const handleServiceChange = async (value) => {
    onServiceChange(value);
    onModelChange(null); // 重置模型选择
    
    // 设置为默认提供商
    try {
      await setDefaultAIProvider(value);
      setCurrentProvider(value);
      message.success(`已设置 ${value} 为默认AI提供商`);
    } catch (error) {
      console.error('设置默认提供商失败:', error);
      message.warning('设置默认提供商失败，但可以继续使用');
    }
  };

  const handleModelChange = (value) => {
    onModelChange(value);
  };

  const handleSettingChange = (key, value) => {
    const newSettings = { ...currentSettings, [key]: value };
    setCurrentSettings(newSettings);
    onSettingsChange(newSettings);
  };

  const getServiceStatusBadge = (providerType) => {
    const status = serviceStatus[providerType];
    if (!status) return <Badge status="default" />;
    
    const statusMap = {
      'active': { status: 'success', text: '在线' },
      'inactive': { status: 'error', text: '离线' },
      'online': { status: 'success', text: '在线' },
      'offline': { status: 'error', text: '离线' },
      'busy': { status: 'warning', text: '忙碌' }
    };
    
    const config = statusMap[status.status] || { status: 'default', text: '未知' };
    return <Badge status={config.status} text={config.text} />;
  };

  return (
    <Card 
      size="small" 
      title={
        <Space>
          <RobotOutlined />
          <span>AI模型配置</span>
        </Space>
      }
      extra={
        <Tooltip title="高级设置">
          <SettingOutlined 
            onClick={() => setShowAdvanced(!showAdvanced)}
            style={{ 
              cursor: 'pointer',
              color: showAdvanced ? '#1890ff' : undefined
            }}
          />
        </Tooltip>
      }
      style={{ marginBottom: 16 }}
    >
      <Spin spinning={loading}>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          {/* AI服务选择 */}
          <div>
            <Row align="middle" style={{ marginBottom: 8 }}>
              <Col>
                <Text strong>AI服务</Text>
                {currentProvider && (
                  <Text type="secondary" style={{ marginLeft: 8 }}>
                    (当前: {currentProvider})
                  </Text>
                )}
              </Col>
              <Col flex="auto" style={{ textAlign: 'right' }}>
                {selectedService && getServiceStatusBadge(selectedService)}
              </Col>
            </Row>
            <Select
              style={{ width: '100%' }}
              placeholder="选择AI服务提供商"
              value={selectedService}
              onChange={handleServiceChange}
              optionLabelProp="label"
            >
              {services.map(service => (
                <Option 
                  key={service.id} 
                  value={service.id}
                  label={service.name}
                >
                  <Space>
                    <ThunderboltOutlined />
                    <span>{service.name}</span>
                    <Text type="secondary">({service.provider})</Text>
                    {service.id === currentProvider && (
                      <Badge count="默认" style={{ backgroundColor: '#52c41a' }} />
                    )}
                  </Space>
                </Option>
              ))}
            </Select>
          </div>

          {/* AI模型选择 */}
          {selectedService && (
            <div>
              <Text strong>AI模型</Text>
              <Select
                style={{ width: '100%', marginTop: 8 }}
                placeholder="选择AI模型"
                value={selectedModel}
                onChange={handleModelChange}
                optionLabelProp="label"
              >
                {models.map(model => (
                  <Option 
                    key={model.id} 
                    value={model.id}
                    label={model.name}
                  >
                    <div>
                      <div>
                        <Text strong>{model.name}</Text>
                      </div>
                      <Paragraph 
                        type="secondary" 
                        style={{ margin: 0, fontSize: '12px' }}
                        ellipsis={{ rows: 1 }}
                      >
                        {model.description}
                      </Paragraph>
                    </div>
                  </Option>
                ))}
              </Select>
            </div>
          )}

          {/* 高级设置 */}
          {showAdvanced && selectedModel && (
            <Card size="small" title="模型参数">
              <Space direction="vertical" style={{ width: '100%' }}>
                {/* 温度设置 */}
                <div>
                  <Row align="middle" justify="space-between">
                    <Col>
                      <Space>
                        <Text>创造性</Text>
                        <Tooltip title="控制回复的随机性和创造性。较高值产生更多样化的回复。">
                          <InfoCircleOutlined />
                        </Tooltip>
                      </Space>
                    </Col>
                    <Col>
                      <InputNumber
                        min={0}
                        max={2}
                        step={0.1}
                        value={currentSettings.temperature}
                        onChange={(value) => handleSettingChange('temperature', value)}
                        style={{ width: 80 }}
                      />
                    </Col>
                  </Row>
                  <Slider
                    min={0}
                    max={2}
                    step={0.1}
                    value={currentSettings.temperature}
                    onChange={(value) => handleSettingChange('temperature', value)}
                    marks={{
                      0: '保守',
                      1: '平衡',
                      2: '创新'
                    }}
                  />
                </div>

                {/* 最大令牌数 */}
                <div>
                  <Row align="middle" justify="space-between">
                    <Col>
                      <Space>
                        <Text>回复长度</Text>
                        <Tooltip title="控制AI回复的最大长度">
                          <InfoCircleOutlined />
                        </Tooltip>
                      </Space>
                    </Col>
                    <Col>
                      <InputNumber
                        min={100}
                        max={4096}
                        step={100}
                        value={currentSettings.maxTokens}
                        onChange={(value) => handleSettingChange('maxTokens', value)}
                        style={{ width: 100 }}
                      />
                    </Col>
                  </Row>
                </div>

                {/* 流式响应 */}
                <Row align="middle" justify="space-between">
                  <Col>
                    <Space>
                      <Text>实时响应</Text>
                      <Tooltip title="启用流式响应，实时显示AI回复过程">
                        <InfoCircleOutlined />
                      </Tooltip>
                    </Space>
                  </Col>
                  <Col>
                    <Switch
                      checked={currentSettings.stream}
                      onChange={(checked) => handleSettingChange('stream', checked)}
                    />
                  </Col>
                </Row>
              </Space>
            </Card>
          )}
        </Space>
      </Spin>
    </Card>
  );
};

export default AIModelSelector;