import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Modal,
  Tabs,
  Card,
  Row,
  Col,
  Select,
  Button,
  Space,
  Tag,
  Divider,
  message,
  Typography,
  Radio
} from 'antd';
import {
  ThunderboltOutlined,
  BgColorsOutlined,
  GlobalOutlined,
  ReloadOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useLanguage } from '../contexts/LanguageContext';
import { getAllProviders, getCurrentProvider, setDefaultProvider } from '../api/ai';

const { Title, Text } = Typography;
const { Option } = Select;

const SettingsModal = ({ visible, onClose }) => {
  const { t, currentLanguage, switchLanguage, availableLanguages } = useLanguage();

  // AI Provider states
  const [aiProviders, setAiProviders] = useState([]);
  const [currentProvider, setCurrentProvider] = useState(null);
  const [loadingProviders, setLoadingProviders] = useState(false);

  // Theme states
  const [currentTheme, setCurrentTheme] = useState('default');
  
  // 使用useMemo避免主题数组在每次渲染时重新创建
  const themes = useMemo(() => [
    { key: 'default', name: t('settings.themes.default'), gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
    { key: 'ocean', name: t('settings.themes.ocean'), gradient: 'linear-gradient(135deg, #2196F3 0%, #00BCD4 100%)' },
    { key: 'sunset', name: t('settings.themes.sunset'), gradient: 'linear-gradient(135deg, #FF5722 0%, #FF9800 100%)' },
    { key: 'forest', name: t('settings.themes.forest'), gradient: 'linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)' },
    { key: 'purple', name: t('settings.themes.purple'), gradient: 'linear-gradient(135deg, #9C27B0 0%, #E91E63 100%)' }
  ], [t]); // 只有当t函数变化时才重新计算

  // Fetch AI providers
  const fetchAIProviders = useCallback(async () => {
    setLoadingProviders(true);
    try {
      const [providersRes, currentProviderRes] = await Promise.all([
        getAllProviders(),
        getCurrentProvider()
      ]);

      if (providersRes.success && providersRes.data) {
        setAiProviders(providersRes.data.providers || []);
      }

      if (currentProviderRes.success && currentProviderRes.data) {
        // 处理API返回的数据，可能是字符串或对象
        if (typeof currentProviderRes.data === 'string') {
          setCurrentProvider({ provider_type: currentProviderRes.data });
        } else {
          setCurrentProvider(currentProviderRes.data);
        }
      } else {
        setCurrentProvider(null);
      }
    } catch (error) {
      console.error('Failed to fetch AI providers:', error);
      message.error(t('messages.loadProvidersFailed'));
    } finally {
      setLoadingProviders(false);
    }
  }, [t]); // 只依赖于t函数

  // Load AI providers on component mount
  useEffect(() => {
    if (visible) {
      fetchAIProviders();
      loadCurrentTheme();
    }
  }, [visible, fetchAIProviders]);

  // Load current theme from localStorage
  const loadCurrentTheme = () => {
    const savedTheme = localStorage.getItem('nuwa-theme') || 'default';
    setCurrentTheme(savedTheme);
  };

  // Handle provider change
  const handleProviderChange = useCallback(async (providerType) => {
    try {
      const response = await setDefaultProvider(providerType);
      if (response.success) {
        message.success(t('messages.providerSwitchSuccess'));
        fetchAIProviders(); // Refresh current provider info
      } else {
        message.error(response.message || 'Failed to switch AI provider');
      }
    } catch (error) {
      console.error('Failed to switch AI provider:', error);
      message.error('Failed to switch AI provider');
    }
  }, [t, fetchAIProviders]);

  // Handle theme change
  const handleThemeChange = useCallback((themeKey) => {
    setCurrentTheme(themeKey);
    localStorage.setItem('nuwa-theme', themeKey);
    
    // Apply theme to CSS variables
    const selectedTheme = themes.find(theme => theme.key === themeKey);
    if (selectedTheme) {
      document.documentElement.style.setProperty('--primary-gradient', selectedTheme.gradient);
      message.success(t('settings.themeChanged'));
    }
  }, [themes, t]);

  const tabItems = [
    {
      key: 'ai',
      label: (
        <Space>
          <ThunderboltOutlined />
          {t('settings.aiSettings')}
        </Space>
      ),
      children: (
        <Card>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Title level={5}>{t('system.currentProvider')}:</Title>
              {currentProvider ? (
                <Tag color="blue" style={{ fontSize: '14px', padding: '4px 8px' }}>
                  {currentProvider.provider_type?.toUpperCase() || 
                   currentProvider.type?.toUpperCase() || 
                   currentProvider.name?.toUpperCase() || 
                   'N/A'}
                </Tag>
              ) : (
                <Tag color="red">{t('settings.notSet')}</Tag>
              )}
            </div>
            
            <Divider />
            
            <div>
              <Title level={5}>{t('system.selectProvider')}:</Title>
              <Select
                style={{ width: '100%' }}
                placeholder={t('settings.selectProvider')}
                value={currentProvider?.provider_type || currentProvider?.type || currentProvider?.name}
                onChange={handleProviderChange}
                loading={loadingProviders}
              >
                {aiProviders.map(provider => (
                  <Option key={provider.type} value={provider.type}>
                    <Space>
                      <Tag 
                        size="small" 
                        color={provider.status === 'active' ? 'green' : 'orange'}
                      >
                        {provider.status === 'active' ? t('settings.available') : t('settings.unavailable')}
                      </Tag>
                      {provider.type.toUpperCase()}
                    </Space>
                  </Option>
                ))}
              </Select>
            </div>

            <Button 
              icon={<ReloadOutlined />} 
              onClick={fetchAIProviders}
              loading={loadingProviders}
            >
              {t('settings.refresh')}
            </Button>
          </Space>
        </Card>
      )
    },
    {
      key: 'system',
      label: (
        <Space>
          <BgColorsOutlined />
          {t('settings.systemSettings')}
        </Space>
      ),
      children: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* Language Settings */}
          <Card title={
            <Space>
              <GlobalOutlined />
              {t('system.language')}
            </Space>
          }>
            <Row gutter={16}>
              <Col span={8}>
                <Text strong>{t('settings.currentLanguage')}:</Text>
              </Col>
              <Col span={16}>
                <Select
                  value={currentLanguage}
                  onChange={switchLanguage}
                  style={{ width: '100%' }}
                >
                  {availableLanguages.map(lang => (
                    <Option key={lang.code} value={lang.code}>
                      <Space>
                        <span>{lang.nativeName}</span>
                        <span style={{ color: '#666' }}>({lang.name})</span>
                      </Space>
                    </Option>
                  ))}
                </Select>
              </Col>
            </Row>
          </Card>

          {/* Theme Settings */}
          <Card title={
            <Space>
              <BgColorsOutlined />
              {t('settings.themeSettings')}
            </Space>
          }>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>{t('settings.currentTheme')}:</Text>
                <div style={{ marginTop: 8 }}>
                  <Radio.Group 
                    value={currentTheme} 
                    onChange={(e) => handleThemeChange(e.target.value)}
                  >
                    {themes.map(theme => (
                      <Radio.Button 
                        key={theme.key} 
                        value={theme.key}
                        style={{ marginBottom: 8, marginRight: 8 }}
                      >
                        <Space>
                          <div 
                            style={{
                              width: 16,
                              height: 16,
                              borderRadius: '50%',
                              background: theme.gradient,
                              border: '1px solid #d9d9d9'
                            }}
                          />
                          {theme.name}
                        </Space>
                      </Radio.Button>
                    ))}
                  </Radio.Group>
                </div>
              </div>
            </Space>
          </Card>
        </Space>
      )
    }
  ];

  return (
    <Modal
      title={
        <Space>
          <SettingOutlined />
          {t('settings.title')}
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
      destroyOnHidden
    >
      <Tabs defaultActiveKey="ai" items={tabItems} />
    </Modal>
  );
};

export default SettingsModal;