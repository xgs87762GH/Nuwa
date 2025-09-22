import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Button, 
  Space, 
  Typography, 
  message,
  Progress,
  Avatar,
  Input,
  List,
  Spin,
  Row,
  Col,
  Select,
  Tag
} from 'antd';
import { 
  StopOutlined,
  RobotOutlined,
  SendOutlined,
  MessageOutlined
} from '@ant-design/icons';
import { createTask } from '../api/tasks';
import { getCurrentProvider, getProviderModels } from '../api/ai';
import { useChat } from '../contexts/ChatContext';
import { useLanguage } from '../contexts/LanguageContext';

const { Text, Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const AIChat = () => {
  const {
    messages,
    addUserMessage,
    addBotMessage,
    setLoading
  } = useChat();

  const { t, currentLanguage } = useLanguage();
  
  // Get theme colors from CSS variables
  const getThemeColors = () => {
    const style = getComputedStyle(document.documentElement);
    return {
      primary: style.getPropertyValue('--primary-gradient') || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      accent: style.getPropertyValue('--bg-primary') || '#667eea',
      surface: 'rgba(255, 255, 255, 0.1)',
      border: 'rgba(255, 255, 255, 0.15)',
      text: 'rgba(255, 255, 255, 0.95)',
      textSecondary: 'rgba(255, 255, 255, 0.8)',
      secondary: style.getPropertyValue('--bg-secondary') || '#764ba2'
    };
  };
  
  const [themeColors, setThemeColors] = useState(getThemeColors());
  
  // Chat states
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentMode, setCurrentMode] = useState('text'); // 'text' or 'voice'
  const [currentModel, setCurrentModel] = useState('Unknown'); // Current AI model
  const [availableModels, setAvailableModels] = useState([]); // Available models for current provider
  
  // 监听主题变化
  useEffect(() => {
    const updateTheme = () => {
      setThemeColors(getThemeColors());
    };
    
    // 监听主题变化事件
    const observer = new MutationObserver(updateTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['style']
    });
    
    return () => observer.disconnect();
  }, []);
  
  // Fetch current AI model and available models
  useEffect(() => {
    const fetchCurrentModel = async () => {
      try {
        const response = await getCurrentProvider();
        if (response.success && response.data) {
          // 处理API返回的数据，可能是字符串或对象
          let providerType;
          if (typeof response.data === 'string') {
            providerType = response.data;
          } else {
            providerType = response.data.provider_type || response.data.name || 'Unknown';
          }
          
          // 获取该提供商的可用模型
          if (providerType && providerType !== 'Unknown') {
            try {
              const modelsResponse = await getProviderModels(providerType);
              if (modelsResponse.success && modelsResponse.data) {
                setAvailableModels(modelsResponse.data);
                setCurrentModel(modelsResponse.data[0] || 'Unknown');
              } else {
                setAvailableModels([]);
              }
            } catch (modelError) {
              console.error('Failed to fetch models for provider:', providerType, modelError);
              setAvailableModels([]);
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch current model:', error);
        setCurrentModel('Unknown');
        setAvailableModels([]);
      }
    };
    
    fetchCurrentModel();
  }, []);
  
  // Voice-related states
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [volume, setVolume] = useState(0);
  
  // Space key long press states
  const [isSpacePressed, setIsSpacePressed] = useState(false);
  const spaceTimeoutRef = useRef(null);
  
  const recognitionRef = useRef(null);
  const speechSynthesisRef = useRef(null);
  const volumeIntervalRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Text-to-speech function
  const speakText = (text) => {
    if (!speechSynthesisRef.current) {
      message.warning(t('messages.noSpeechSupport'));
      return;
    }

    // Stop current speech
    speechSynthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = currentLanguage === 'zh' ? 'zh-CN' : 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => {
      setIsSpeaking(false);
      message.error(t('messages.speechSynthesisFailed'));
    };

    speechSynthesisRef.current.speak(utterance);
  };

  // Send message function
  const handleSendMessage = useCallback(async (text) => {
    const messageText = text || inputText.trim();
    if (!messageText) return;

    setIsProcessing(true);
    setLoading(true);
    setInputText('');
    
    // Add user message
    addUserMessage(messageText);
    
    try {
      const response = await createTask(messageText);
      
      if (response.success && response.data) {
        const botReply = response.data.result || response.message || t('common.success');
        
        // Add AI reply
        addBotMessage(botReply, {
          taskId: response.data.task_id,
          processedBy: response.data.processed_by,
          timestamp: new Date().toISOString(),
          model: currentModel
        });
        
        // If in voice mode, speak the reply
        if (currentMode === 'voice') {
          speakText(botReply);
        }
        
        message.success(t('messages.sendSuccess'));
      } else {
        // Handle business logic errors (e.g., no suitable plugin found)
        const errorMsg = response.message || t('common.error');
        const fullErrorMsg = t('aiChat.errorRetryMessage', { error: errorMsg });
        
        addBotMessage(fullErrorMsg, {
          error: true,
          timestamp: new Date().toISOString(),
          originalError: response.message
        });
        
        if (currentMode === 'voice') {
          speakText(fullErrorMsg);
        }
        
        message.warning(errorMsg);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMsg = t('aiChat.processErrorMessage');
      
      addBotMessage(errorMsg);
      
      if (currentMode === 'voice') {
        speakText(errorMsg);
      }
      
      message.error(t('messages.sendFailed'));
    } finally {
      setIsProcessing(false);
      setLoading(false);
    }
  }, [inputText, currentMode, addUserMessage, addBotMessage, setLoading, t, currentLanguage, speakText, currentModel]);

  // Auto scroll to latest message
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Initialize speech recognition
  useEffect(() => {
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = currentLanguage === 'zh' ? 'zh-CN' : 'en-US';

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setTranscript(finalTranscript);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        message.error('Speech recognition failed, please try again');
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        if (transcript) {
          handleSendMessage(transcript);
          setTranscript('');
        }
      };
    }

    // Initialize speech synthesis
    if (window.speechSynthesis) {
      speechSynthesisRef.current = window.speechSynthesis;
    }

    return () => {
      if (volumeIntervalRef.current) {
        clearInterval(volumeIntervalRef.current);
      }
    };
  }, [transcript, handleSendMessage, currentLanguage]);

  // Start speech recognition
  const startListening = () => {
    if (!recognitionRef.current) {
      message.warning('Your browser does not support speech recognition');
      return;
    }

    setIsListening(true);
    setTranscript('');
    recognitionRef.current.start();

    // 模拟音量检测
    volumeIntervalRef.current = setInterval(() => {
      setVolume(Math.random() * 100);
    }, 100);
  };

  // Stop speech recognition
  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
    if (volumeIntervalRef.current) {
      clearInterval(volumeIntervalRef.current);
      setVolume(0);
    }
  };

  // Stop speech synthesis
  const stopSpeaking = () => {
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  // Handle space key long press for voice input
  const handleSpaceKeyDown = useCallback((e) => {
    if (e.code === 'Space' && !isSpacePressed && !isProcessing) {
      // 只有在输入框没有焦点时才阻止默认行为
      const activeElement = document.activeElement;
      const isInputFocused = activeElement && (
        activeElement.tagName === 'INPUT' || 
        activeElement.tagName === 'TEXTAREA' ||
        activeElement.contentEditable === 'true'
      );
      
      if (!isInputFocused) {
        e.preventDefault();
        setIsSpacePressed(true);
        
        // Start voice recording after 2000ms hold (2 seconds)
        spaceTimeoutRef.current = setTimeout(() => {
          setCurrentMode('voice');
          startListening();
        }, 2000);
      }
    }
  }, [isSpacePressed, isProcessing]);

  const handleSpaceKeyUp = useCallback((e) => {
    if (e.code === 'Space' && isSpacePressed) {
      // 只有在输入框没有焦点时才阻止默认行为
      const activeElement = document.activeElement;
      const isInputFocused = activeElement && (
        activeElement.tagName === 'INPUT' || 
        activeElement.tagName === 'TEXTAREA' ||
        activeElement.contentEditable === 'true'
      );
      
      if (!isInputFocused) {
        e.preventDefault();
      }
      
      setIsSpacePressed(false);
      
      // Clear timeout if released before 2000ms
      if (spaceTimeoutRef.current) {
        clearTimeout(spaceTimeoutRef.current);
        spaceTimeoutRef.current = null;
      }
      
      // If voice mode was activated, stop recording and send
      if (isListening) {
        stopListening();
        // Auto-send after stopping recording
        setTimeout(() => {
          if (transcript.trim()) {
            handleSendMessage(transcript);
            setTranscript('');
          }
          setCurrentMode('text');
        }, 100);
      }
    }
  }, [isSpacePressed, isListening, transcript, handleSendMessage]);

  // Add keyboard event listeners
  useEffect(() => {
    const handleKeyDown = (e) => handleSpaceKeyDown(e);
    const handleKeyUp = (e) => handleSpaceKeyUp(e);
    
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
      if (spaceTimeoutRef.current) {
        clearTimeout(spaceTimeoutRef.current);
      }
    };
  }, [handleSpaceKeyDown, handleSpaceKeyUp]);

  // Render messages list
  const renderMessages = () => (
    <div style={{ 
      overflowY: 'auto', 
      padding: '20px', 
      minHeight: '300px',
      background: themeColors.background
    }}>
      {messages.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '80px 20px',
          background: 'transparent'
        }}>
          <div style={{ 
            fontSize: '48px', 
            marginBottom: '24px',
            opacity: 0.6 
          }}>
            🤖
          </div>
          <Title level={3} style={{ 
            color: themeColors.text, 
            marginBottom: '16px',
            fontWeight: '600'
          }}>
            {t('aiChat.welcome')}
          </Title>
          <Text style={{ 
            color: themeColors.textSecondary, 
            fontSize: '16px', 
            lineHeight: '1.6' 
          }}>
            {t('aiChat.welcomeMessage')}
          </Text>
        </div>
      ) : (
        <List
          dataSource={messages}
          renderItem={(message, index) => (
            <List.Item
              key={index}
              style={{
                justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                border: 'none',
                padding: '12px 0',
                marginBottom: '8px'
              }}
            >
              <div
                style={{
                  maxWidth: '75%',
                  padding: '16px 20px',
                  borderRadius: message.type === 'user' ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
                  background: message.type === 'user' 
                    ? themeColors.primary
                    : themeColors.surface,
                  border: message.type === 'user' 
                    ? 'none'
                    : `1px solid ${themeColors.border}`,
                  boxShadow: message.type === 'user' 
                    ? `0 4px 12px ${themeColors.accent}30`
                    : '0 4px 12px rgba(0, 0, 0, 0.15)',
                  color: message.type === 'user' ? 'white' : themeColors.text,
                  position: 'relative'
                }}
              >
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px',
                  marginBottom: '8px'
                }}>
                  <Avatar 
                    size="small" 
                    icon={message.type === 'user' ? <MessageOutlined /> : <RobotOutlined />}
                    style={{ 
                      background: message.type === 'user' ? themeColors.accent : themeColors.secondary,
                      border: '2px solid rgba(255, 255, 255, 0.2)'
                    }}
                  />
                  <Text style={{ 
                    color: message.type === 'user' ? 'rgba(255, 255, 255, 0.9)' : themeColors.text, 
                    fontSize: '13px',
                    fontWeight: '500'
                  }}>
                    {message.type === 'user' ? t('aiChat.user') : t('aiChat.assistant')}
                  </Text>
                  <Text style={{ 
                    color: message.type === 'user' ? 'rgba(255, 255, 255, 0.6)' : themeColors.textSecondary, 
                    fontSize: '11px'
                  }}>
                    {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </Text>
                </div>
                
                <div style={{
                  color: message.type === 'user' ? 'white' : themeColors.text,
                  fontSize: '14px',
                  lineHeight: '1.6',
                  wordBreak: 'break-word'
                }}>
                  {message.content}
                </div>
                
                {message.metadata && message.metadata.taskId && (
                  <div style={{ 
                    marginTop: '12px',
                    padding: '8px 12px',
                    background: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}>
                    <Text style={{ 
                      color: message.type === 'user' ? 'rgba(255, 255, 255, 0.8)' : themeColors.textSecondary
                    }}>
                      {t('aiChat.taskId')}: {message.metadata.taskId}
                    </Text>
                  </div>
                )}
              </div>
            </List.Item>
          )}
        />
      )}
      
      {/* Processing Indicator */}
      {isProcessing && (
        <div style={{ 
          display: 'flex', 
          alignItems: 'flex-start',
          gap: '12px',
          marginBottom: '24px',
          justifyContent: 'flex-start'
        }}>
          {/* AI Avatar */}
          <Avatar 
            size="small" 
            icon={<RobotOutlined />}
            style={{ 
              background: themeColors.secondary,
              border: '2px solid rgba(255, 255, 255, 0.2)'
            }}
          />

          {/* Thinking Animation */}
          <div style={{
            background: themeColors.surface,
            border: `1px solid ${themeColors.border}`,
            borderRadius: '20px 20px 20px 4px',
            padding: '16px 20px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Spin size="small" />
            <Text style={{ 
              color: themeColors.textSecondary,
              fontSize: '14px'
            }}>
              {t('aiChat.thinking')}
            </Text>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );

  return (
    <div 
      style={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        background: themeColors.background
      }}
    >
      {/* Header */}
      <div style={{
        padding: '20px 24px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexShrink: 0,
        background: 'rgba(255, 255, 255, 0.02)'
      }}>
        <Space>
          <RobotOutlined style={{ color: themeColors.accent, fontSize: '20px' }} />
          <Text style={{ color: 'white', fontSize: '18px', fontWeight: '600' }}>
            {t('aiChat.title')}
          </Text>
          <Tag 
            color={isListening ? 'orange' : 'green'} 
            style={{ 
              borderRadius: '12px',
              padding: '2px 8px',
              fontSize: '11px',
              fontWeight: '500'
            }}
          >
            {isListening ? '🎤 Recording' : currentMode === 'voice' ? t('aiChat.voiceMode') : t('aiChat.textMode')}
          </Tag>
          {isSpacePressed && (
            <Tag color="blue" style={{ borderRadius: '12px', fontSize: '11px' }}>
              Hold Space (2s)...
            </Tag>
          )}
        </Space>
        
        <Space>
          {isSpeaking && (
            <Button
              size="small"
              icon={<StopOutlined />}
              onClick={stopSpeaking}
              type="text"
              style={{ 
                color: 'white',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px'
              }}
            >
              {t('aiChat.stopSpeaking')}
            </Button>
          )}
        </Space>
      </div>

      {/* Messages Container */}
      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        maxHeight: 'calc(100% - 220px)',
        background: themeColors.background
      }}>
        {renderMessages()}
      </div>
      
      {/* Input Area */}
      <div style={{ 
        padding: '20px 24px',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        background: 'rgba(255, 255, 255, 0.03)',
        flexShrink: 0
      }}>
        {/* Voice Status Display */}
        {isListening && (
          <div style={{ 
            marginBottom: '16px', 
            padding: '16px',
            background: 'rgba(251, 146, 60, 0.1)',
            border: '1px solid rgba(251, 146, 60, 0.3)',
            borderRadius: '12px',
            textAlign: 'center'
          }}>
            <Text style={{ 
              color: '#fb923c', 
              display: 'block', 
              marginBottom: '12px', 
              fontSize: '15px',
              fontWeight: '500'
            }}>
              🎤 {t('aiChat.listening')}
            </Text>
            <Progress 
              percent={volume} 
              showInfo={false} 
              strokeColor="#fb923c"
              style={{ maxWidth: '300px', margin: '0 auto' }}
            />
            {transcript && (
              <Text style={{ 
                color: 'white', 
                fontSize: '13px', 
                display: 'block', 
                marginTop: '12px',
                padding: '8px 12px',
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                fontStyle: 'italic'
              }}>
                "{transcript}"
              </Text>
            )}
          </div>
        )}

        {/* Model Selection Row */}
        <Row gutter={[12, 12]} align="middle" style={{ marginBottom: '12px' }}>
          <Col flex="auto">
            <Space style={{ width: '100%', justifyContent: 'space-between' }}>
              <Text style={{ color: themeColors.textSecondary, fontSize: '13px' }}>
                {t('aiChat.currentModel')}
              </Text>
              <Select
                value={currentModel}
                onChange={setCurrentModel}
                style={{ 
                  minWidth: '180px'
                }}
                size="small"
                className="nuwa-model-select"
                placeholder={t('aiChat.selectModel')}
                notFoundContent={t('aiChat.noModelsAvailable')}
                dropdownStyle={{
                  background: 'rgba(30, 41, 59, 0.95)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              >
                {availableModels.length > 0 ? (
                  availableModels.map(model => (
                    <Option 
                      key={model} 
                      value={model}
                      style={{
                        background: 'transparent',
                        color: 'white'
                      }}
                    >
                      {model}
                    </Option>
                  ))
                ) : (
                  <Option 
                    key={currentModel} 
                    value={currentModel}
                    style={{
                      background: 'transparent',
                      color: 'white'
                    }}
                  >
                    {currentModel}
                  </Option>
                )}
              </Select>
            </Space>
          </Col>
        </Row>

        {/* Input Row */}
        <Row gutter={[16, 12]} align="middle">
          <Col xs={24} sm={20} md={22} flex="auto">
            <TextArea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={`${t('aiChat.inputPlaceholder')} • Hold Space for voice input`}
              autoSize={{ minRows: 2, maxRows: 4 }}
              style={{
                background: 'rgba(255, 255, 255, 0.08)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                borderRadius: '12px',
                color: 'white',
                resize: 'none',
                fontSize: '14px',
                padding: '12px 16px'
              }}
              onPressEnter={(e) => {
                if (e.shiftKey) return;
                e.preventDefault();
                handleSendMessage();
              }}
            />
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={() => handleSendMessage()}
              loading={isProcessing}
              disabled={!inputText.trim()}
              size="large"
              style={{
                height: '52px',
                width: '52px',
                background: themeColors.primary,
                border: 'none',
                borderRadius: '12px',
                boxShadow: `0 4px 12px ${themeColors.accent}40`
              }}
            />
          </Col>
        </Row>

        {/* Tips */}
        <div style={{ 
          marginTop: '12px', 
          textAlign: 'center'
        }}>
          <Text style={{ 
            color: 'rgba(255, 255, 255, 0.5)', 
            fontSize: '12px' 
          }}>
            Hold Space for 2s for voice • Shift+Enter for new line • Enter to send
          </Text>
        </div>
      </div>
    </div>
  );
};

export default AIChat;