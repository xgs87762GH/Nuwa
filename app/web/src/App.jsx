import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import { 
  HomeOutlined, 
  ToolOutlined, 
  DesktopOutlined, 
  UnorderedListOutlined  // 使用 UnorderedListOutlined 替代 TasksOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import Tasks from './pages/Tasks';
import Tools from './pages/Tools';
import System from './pages/System';
import FloatingChatBot from './components/FloatingChatBot';
import { ChatProvider } from './contexts/ChatContext';

const { Header, Content, Sider } = Layout;

const App = () => {
  const location = useLocation();
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/tasks',
      icon: <UnorderedListOutlined />,  // 修改这里
      label: <Link to="/tasks">任务管理</Link>,
    },
    {
      key: '/tools',
      icon: <ToolOutlined />,
      label: <Link to="/tools">工具管理</Link>,
    },
    {
      key: '/system',
      icon: <DesktopOutlined />,
      label: <Link to="/system">系统监控</Link>,
    },
  ];

  return (
    <ChatProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider collapsible>
          <div className="logo" style={{ 
            height: 32, 
            margin: 16, 
            background: 'rgba(255, 255, 255, 0.3)',
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold'
          }}>
            Nuwa
          </div>
          <Menu
            theme="dark"
            selectedKeys={[location.pathname]}
            mode="inline"
            items={menuItems}
          />
        </Sider>
        <Layout>
          <Header style={{ 
            padding: 0, 
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            paddingLeft: 24
          }}>
            <h1 style={{ margin: 0, fontSize: 20 }}>智能AI插件管理和任务调度平台</h1>
          </Header>
          <Content style={{ margin: '16px' }}>
            <div style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: 8,
            }}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/tasks" element={<Tasks />} />
                <Route path="/tools" element={<Tools />} />
                <Route path="/system" element={<System />} />
              </Routes>
            </div>
          </Content>
        </Layout>
        
        {/* 全局悬浮聊天机器人 */}
        <FloatingChatBot />
      </Layout>
    </ChatProvider>
  );
};

export default App;