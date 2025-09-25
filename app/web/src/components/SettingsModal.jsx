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
    { key: 'default', name: t('settings.themes.default'), gradient: 'var(--theme-gradient, linear-gradient(135deg, #667eea 0%, #764ba2 100%))' },
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
  const loadCurrentTheme = useCallback(() => {
    const savedTheme = localStorage.getItem('nuwa-theme') || 'default';
    setCurrentTheme(savedTheme);
    
    // Apply theme on load
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // 为了兼容性，设置对应的 CSS 变量 - 使用硬编码的映射避免依赖问题
    const themeGradients = {
      'default': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      'ocean': 'linear-gradient(135deg, #2196F3 0%, #00BCD4 100%)',
      'sunset': 'linear-gradient(135deg, #FF5722 0%, #FF9800 100%)',
      'forest': 'linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)',
      'purple': 'linear-gradient(135deg, #9C27B0 0%, #E91E63 100%)'
    };
    
    const gradient = themeGradients[savedTheme] || themeGradients['default'];
    document.documentElement.style.setProperty('--primary-gradient', gradient);
  }, []);

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
    
    // Apply theme by setting data-theme attribute
    document.documentElement.setAttribute('data-theme', themeKey);
    
    // 为了兼容性，仍然设置 CSS 变量
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
        <div className="settings-ai-section">
          <div className="settings-card">
            <div className="current-provider-section">
              <div className="section-header">
                <ThunderboltOutlined className="section-icon" />
                <Text className="section-title">{t('system.currentProvider')}</Text>
              </div>
              <div className="provider-badge">
                {currentProvider ? (
                  <div className="provider-active">
                    <div className="provider-status-indicator active"></div>
                    <span className="provider-name">
                      {currentProvider.provider_type?.toUpperCase() || 
                       currentProvider.type?.toUpperCase() || 
                       currentProvider.name?.toUpperCase() || 
                       'N/A'}
                    </span>
                  </div>
                ) : (
                  <div className="provider-inactive">
                    <div className="provider-status-indicator inactive"></div>
                    <span className="provider-name">{t('settings.notSet')}</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="provider-select-section">
              <div className="section-header">
                <SettingOutlined className="section-icon" />
                <Text className="section-title">{t('system.selectProvider')}</Text>
              </div>
              <Select
                className="provider-selector"
                placeholder={t('settings.selectProvider')}
                value={currentProvider?.provider_type || currentProvider?.type || currentProvider?.name}
                onChange={handleProviderChange}
                loading={loadingProviders}
                size="large"
                dropdownClassName="provider-dropdown"
              >
                {aiProviders.map(provider => (
                  <Option key={provider.type} value={provider.type}>
                    <div className="provider-option">
                      <div className={`provider-status-dot ${provider.status === 'active' ? 'active' : 'inactive'}`}></div>
                      <span className="provider-type">{provider.type.toUpperCase()}</span>
                      <span className={`provider-status-text ${provider.status}`}>
                        {provider.status === 'active' ? t('settings.available') : t('settings.unavailable')}
                      </span>
                    </div>
                  </Option>
                ))}
              </Select>
            </div>

            <div className="refresh-section">
              <Button 
                className="refresh-button"
                icon={<ReloadOutlined />} 
                onClick={fetchAIProviders}
                loading={loadingProviders}
                size="large"
                type="primary"
                ghost
              >
                {t('settings.refresh')}
              </Button>
            </div>
          </div>
        </div>
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
        <div className="settings-system-section">
          {/* Language Settings */}
          <div className="settings-card">
            <div className="card-header">
              <GlobalOutlined className="header-icon" />
              <Text className="header-title">{t('system.language')}</Text>
            </div>
            <div className="language-content">
              <div className="current-language">
                <Text className="label-text">{t('settings.currentLanguage')}</Text>
                <div className="language-display">
                  {availableLanguages.find(lang => lang.code === currentLanguage)?.nativeName || currentLanguage}
                </div>
              </div>
              <Select
                className="language-selector"
                value={currentLanguage}
                onChange={switchLanguage}
                size="large"
                dropdownClassName="language-dropdown"
              >
                {availableLanguages.map(lang => (
                  <Option key={lang.code} value={lang.code}>
                    <div className="language-option">
                      <span className="native-name">{lang.nativeName}</span>
                      <span className="english-name">({lang.name})</span>
                    </div>
                  </Option>
                ))}
              </Select>
            </div>
          </div>

          {/* Theme Settings */}
          <div className="settings-card">
            <div className="card-header">
              <BgColorsOutlined className="header-icon" />
              <Text className="header-title">{t('settings.themeSettings')}</Text>
            </div>
            <div className="theme-content">
              <div className="current-theme">
                <Text className="label-text">{t('settings.currentTheme')}</Text>
                <div className="theme-display">
                  {themes.find(theme => theme.key === currentTheme)?.name || 'Default'}
                </div>
              </div>
              <div className="theme-selector">
                <Radio.Group 
                  value={currentTheme} 
                  onChange={(e) => handleThemeChange(e.target.value)}
                  className="theme-radio-group"
                >
                  {themes.map(theme => (
                    <Radio.Button 
                      key={theme.key} 
                      value={theme.key}
                      className="theme-radio-button"
                    >
                      <div className="theme-option">
                        <div 
                          className="theme-preview"
                          style={{
                            background: theme.gradient,
                          }}
                        />
                        <span className="theme-name">{theme.name}</span>
                      </div>
                    </Radio.Button>
                  ))}
                </Radio.Group>
              </div>
            </div>
          </div>
        </div>
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