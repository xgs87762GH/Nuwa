import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Menu, Typography, Button } from 'antd';
import { 
  HomeOutlined, 
  ToolOutlined, 
  DesktopOutlined, 
  UnorderedListOutlined,
  RobotOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import Tasks from './pages/Tasks';
import Tools from './pages/Tools';
import System from './pages/System';
import FloatingChatBot from './components/FloatingChatBot';
import SettingsModal from './components/SettingsModal';
import { ChatProvider } from './contexts/ChatContext';
import { LanguageProvider, useLanguage } from './contexts/LanguageContext';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

const AppContent = () => {
  const location = useLocation();
  const { t, currentLanguage } = useLanguage();
  const [settingsVisible, setSettingsVisible] = React.useState(false);

  // 初始化主题
  React.useEffect(() => {
    const initializeTheme = () => {
      const savedTheme = localStorage.getItem('nuwa-theme') || 'default';
      document.documentElement.setAttribute('data-theme', savedTheme);
      
      // 为了兼容性，设置对应的 CSS 变量
      const themeGradients = {
        'default': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'ocean': 'linear-gradient(135deg, #2196F3 0%, #00BCD4 100%)',
        'sunset': 'linear-gradient(135deg, #FF5722 0%, #FF9800 100%)',
        'forest': 'linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)',
        'purple': 'linear-gradient(135deg, #9C27B0 0%, #E91E63 100%)'
      };
      
      const gradient = themeGradients[savedTheme] || themeGradients['default'];
      document.documentElement.style.setProperty('--primary-gradient', gradient);
    };
    
    initializeTheme();
  }, []);

  // Show settings modal
  const showSettings = () => {
    setSettingsVisible(true);
  };

  // Hide settings modal
  const hideSettings = () => {
    setSettingsVisible(false);
  };

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/" style={{ color: 'inherit' }}>{t('navigation.home')}</Link>,
    },
    {
      key: '/tasks',
      icon: <UnorderedListOutlined />,
      label: <Link to="/tasks" style={{ color: 'inherit' }}>{t('navigation.tasks')}</Link>,
    },
    {
      key: '/tools',
      icon: <ToolOutlined />,
      label: <Link to="/tools" style={{ color: 'inherit' }}>{t('navigation.tools')}</Link>,
    },
    {
      key: '/system',
      icon: <DesktopOutlined />,
      label: <Link to="/system" style={{ color: 'inherit' }}>{t('navigation.system')}</Link>,
    },
  ];

  return (
    <ChatProvider>
      <div className="nuwa-container">
        <Layout style={{ minHeight: '100vh', background: 'transparent' }}>
          <Sider
            width={250}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '0 20px 20px 0',
              margin: '20px 0 20px 20px',
              height: 'calc(100vh - 40px)',
              position: 'fixed',
              zIndex: 100
            }}
          >
            <div style={{ 
              padding: '20px',
              textAlign: 'center',
              borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
              marginBottom: '20px'
            }}>
              <RobotOutlined style={{ 
                fontSize: '32px', 
                color: 'white',
                marginBottom: '8px',
                display: 'block'
              }} />
              <Title level={4} style={{ 
                color: 'white', 
                margin: 0,
                fontWeight: 'bold',
                textShadow: '0 2px 4px rgba(0,0,0,0.3)'
              }}>
                Nuwa AI
              </Title>
              <div style={{ 
                color: 'rgba(255, 255, 255, 0.7)', 
                fontSize: '12px',
                marginTop: '4px'
              }}>
                {t('common.platform')}
              </div>
            </div>
            <Menu
              mode="vertical"
              selectedKeys={[location.pathname]}
              items={menuItems}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'white'
              }}
              theme="dark"
            />

            {/* Settings Button */}
            <div style={{
              position: 'absolute',
              bottom: '20px',
              left: '20px',
              right: '20px'
            }}>
              <Button
                type="primary"
                icon={<SettingOutlined />}
                onClick={showSettings}
                style={{
                  width: '100%',
                  background: 'rgba(255, 255, 255, 0.1)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  backdropFilter: 'blur(10px)'
                }}
              >
                {t('navigation.settings')}
              </Button>
            </div>
          </Sider>

          <Layout style={{ 
            marginLeft: 290, 
            background: 'transparent',
            padding: '20px 20px 20px 0'
          }}>
            <Header style={{
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '20px',
              marginBottom: '20px',
              padding: '0 32px',
              height: '70px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <Title level={3} style={{ 
                color: 'white', 
                margin: 0,
                textShadow: '0 2px 4px rgba(0,0,0,0.3)'
              }}>
                {(() => {
                  const currentItem = menuItems.find(item => item.key === location.pathname);
                  if (currentItem && currentItem.label && currentItem.label.props) {
                    return currentItem.label.props.children;
                  }
                  return t('navigation.home');
                })()}
              </Title>
              <div style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                {new Date().toLocaleString(currentLanguage === 'zh' ? 'zh-CN' : 'en-US')}
              </div>
            </Header>

            <Content style={{
              background: 'transparent',
              borderRadius: '20px',
              overflow: 'hidden'
            }}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/tasks" element={<Tasks />} />
                <Route path="/tools" element={<Tools />} />
                <Route path="/system" element={<System />} />
              </Routes>
            </Content>
          </Layout>

          <FloatingChatBot />
          <SettingsModal visible={settingsVisible} onClose={hideSettings} />
        </Layout>
      </div>
    </ChatProvider>
  );
};

const App = () => {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
};

export default App;