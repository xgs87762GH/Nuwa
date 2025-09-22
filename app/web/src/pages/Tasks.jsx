import React, { useState, useRef, useEffect } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  message, 
  Typography, 
  Space, 
  Avatar, 
  Spin,
  Tooltip,
  Modal,
  Drawer
} from 'antd';
import { 
  SendOutlined, 
  AudioOutlined, 
  UserOutlined, 
  RobotOutlined,
  SoundOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { createTask } from '../api/tasks';
import { createChatTask } from '../api/ai';
import { useChat } from '../contexts/ChatContext';
import AIModelSelector from '../components/AIModelSelector';

const { TextArea } = Input;
const { Title, Text } = Typography;

const Tasks = () => {
  const {
    messages,
    isLoading,
    addUserMessage,
    addBotMessage,
    setLoading,
    startSession
  } = useChat();
  
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [settingsDrawerVisible, setSettingsDrawerVisible] = useState(false);
  const [selectedService, setSelectedService] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [aiSettings, setAISettings] = useState({
    temperature: 0.7,
    maxTokens: 2048,
    stream: false
  });
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 开始会话
  useEffect(() => {
    startSession();
  }, []);

  // 语音识别初始化
  useEffect(() => {
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'zh-CN';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = () => {
        setIsListening(false);
        message.error('语音识别失败，请重试');
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // 添加用户消息
    addUserMessage(inputValue);
    const userInput = inputValue;
    setInputValue('');
    setLoading(true);

    try {
      let response;
      
      // 如果选择了AI服务和模型，使用新的聊天API
      if (selectedService && selectedModel) {
        response = await createChatTask(userInput, {
          serviceId: selectedService,
          modelId: selectedModel,
          ...aiSettings
        });
      } else {
        // 否则使用原有的任务API
        response = await createTask(userInput);
      }
      
      // 添加机器人回复
      addBotMessage(
        response.message || response.content || '任务已创建成功！',
        response
      );
    } catch (error) {
      console.error('发送消息失败:', error);
      addBotMessage('抱歉，处理您的请求时出现了错误，请稍后重试。');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startVoiceRecognition = () => {
    if (recognitionRef.current) {
      setIsListening(true);
      recognitionRef.current.start();
    } else {
      message.warning('您的浏览器不支持语音识别功能');
    }
  };

  const formatTime = (date) => {
    // 确保date是一个有效的Date对象
    if (!date) return '刚刚';
    
    const dateObj = date instanceof Date ? date : new Date(date);
    
    // 检查日期是否有效
    if (isNaN(dateObj.getTime())) return '刚刚';
    
    return dateObj.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessage = (msg) => {
    // 安全检查
    if (!msg || typeof msg !== 'object') return null;
    
    const isBot = msg.type === 'bot';
    
    return (
      <div 
        key={msg.id || Math.random()} 
        style={{ 
          display: 'flex', 
          justifyContent: isBot ? 'flex-start' : 'flex-end',
          marginBottom: 16,
          alignItems: 'flex-start'
        }}
      >
        {isBot && (
          <Avatar 
            icon={<RobotOutlined />} 
            style={{ 
              backgroundColor: '#1890ff',
              marginRight: 8,
              flexShrink: 0
            }} 
          />
        )}
        
        <div style={{ 
          maxWidth: '70%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: isBot ? 'flex-start' : 'flex-end'
        }}>
          <div
            style={{
              background: isBot ? '#f5f5f5' : '#1890ff',
              color: isBot ? '#000' : '#fff',
              padding: '8px 12px',
              borderRadius: '12px',
              borderTopLeftRadius: isBot ? '4px' : '12px',
              borderTopRightRadius: isBot ? '12px' : '4px',
              wordWrap: 'break-word'
            }}
          >
            {msg.content || '消息内容为空'}
          </div>
          <Text 
            type="secondary" 
            style={{ 
              fontSize: '12px', 
              marginTop: 4,
              textAlign: isBot ? 'left' : 'right'
            }}
          >
            {formatTime(msg.timestamp)}
          </Text>
        </div>

        {!isBot && (
          <Avatar 
            icon={<UserOutlined />} 
            style={{ 
              backgroundColor: '#52c41a',
              marginLeft: 8,
              flexShrink: 0
            }} 
          />
        )}
      </div>
    );
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: 16 
      }}>
        <Title level={2} style={{ margin: 0 }}>AI 助手</Title>
        <Space>
          {selectedService && selectedModel && (
            <Tooltip title={`使用 ${selectedService}/${selectedModel}`}>
              <RobotOutlined style={{ color: '#52c41a' }} />
            </Tooltip>
          )}
          <Tooltip title="AI模型设置">
            <Button 
              icon={<SettingOutlined />}
              onClick={() => setSettingsDrawerVisible(true)}
              type={selectedService && selectedModel ? 'primary' : 'default'}
            >
              模型配置
            </Button>
          </Tooltip>
        </Space>
      </div>
      
      <Card 
        style={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column',
          height: 'calc(100vh - 160px)'
        }}
        bodyStyle={{ 
          padding: 0, 
          display: 'flex', 
          flexDirection: 'column',
          height: '100%'
        }}
      >
        {/* 消息列表 */}
        <div 
          style={{ 
            flex: 1, 
            padding: '16px', 
            overflowY: 'auto',
            maxHeight: 'calc(100vh - 260px)'
          }}
        >
          {Array.isArray(messages) && messages.map(renderMessage)}
          {isLoading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 16 }}>
              <Avatar 
                icon={<RobotOutlined />} 
                style={{ backgroundColor: '#1890ff', marginRight: 8 }} 
              />
              <div style={{ 
                background: '#f5f5f5',
                padding: '8px 12px',
                borderRadius: '12px',
                borderTopLeftRadius: '4px'
              }}>
                <Spin size="small" /> <Text type="secondary">正在思考...</Text>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div style={{ 
          padding: '16px', 
          borderTop: '1px solid #f0f0f0',
          background: '#fafafa'
        }}>
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的消息... (按Enter发送，Shift+Enter换行)"
              autoSize={{ minRows: 1, maxRows: 4 }}
              style={{ resize: 'none' }}
            />
            <Tooltip title="语音输入">
              <Button
                icon={<SoundOutlined />}
                onClick={startVoiceRecognition}
                loading={isListening}
                type={isListening ? 'primary' : 'default'}
                style={{ height: 'auto' }}
              />
            </Tooltip>
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              style={{ height: 'auto' }}
            >
              发送
            </Button>
          </Space.Compact>
        </div>
      </Card>

      {/* AI模型配置抽屉 */}
      <Drawer
        title="AI模型配置"
        placement="right"
        width={400}
        onClose={() => setSettingsDrawerVisible(false)}
        open={settingsDrawerVisible}
        bodyStyle={{ padding: 16 }}
      >
        <AIModelSelector
          selectedService={selectedService}
          selectedModel={selectedModel}
          onServiceChange={setSelectedService}
          onModelChange={setSelectedModel}
          onSettingsChange={setAISettings}
          settings={aiSettings}
        />
      </Drawer>
    </div>
  );
};

export default Tasks;