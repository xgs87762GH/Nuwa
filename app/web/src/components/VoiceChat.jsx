import React, { useState, useRef, useEffect } from 'react';
import { 
  Button, 
  Space, 
  Card, 
  Typography, 
  message,
  Progress,
  Avatar
} from 'antd';
import { 
  AudioOutlined, 
  SoundOutlined,
  StopOutlined,
  PlayCircleOutlined,
  RobotOutlined,
  CustomerServiceOutlined
} from '@ant-design/icons';
import { createTask } from '../api/tasks';
import { useChat } from '../contexts/ChatContext';

const { Title, Text, Paragraph } = Typography;

const VoiceChat = () => {
  const {
    addUserMessage,
    addBotMessage,
    setLoading
  } = useChat();
  
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [volume, setVolume] = useState(0);
  
  const recognitionRef = useRef(null);
  const speechSynthesisRef = useRef(null);
  const volumeIntervalRef = useRef(null);

  // 初始化语音识别
  useEffect(() => {
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'zh-CN';

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
        console.error('语音识别错误:', event.error);
        setIsListening(false);
        message.error('语音识别失败，请重试');
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        if (transcript) {
          handleProcessVoice(transcript);
        }
      };
    }

    // 初始化语音合成
    if (window.speechSynthesis) {
      speechSynthesisRef.current = window.speechSynthesis;
    }

    return () => {
      if (volumeIntervalRef.current) {
        clearInterval(volumeIntervalRef.current);
      }
    };
  }, [transcript]);

  // 开始语音识别
  const startListening = () => {
    if (!recognitionRef.current) {
      message.warning('您的浏览器不支持语音识别功能');
      return;
    }

    setIsListening(true);
    setTranscript('');
    setResponse('');
    recognitionRef.current.start();

    // 模拟音量检测
    volumeIntervalRef.current = setInterval(() => {
      setVolume(Math.random() * 100);
    }, 100);
  };

  // 停止语音识别
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

  // 处理语音输入
  const handleProcessVoice = async (text) => {
    setIsProcessing(true);
    setLoading(true);
    
    // 添加用户消息到聊天记录
    addUserMessage(text);
    
    try {
      const result = await createTask(text);
      const responseText = result.message || '已经为您处理了这个请求。';
      setResponse(responseText);
      
      // 添加机器人回复到聊天记录
      addBotMessage(responseText, result);
      
      // 语音播报回复
      speakText(responseText);
    } catch (error) {
      console.error('处理语音请求失败:', error);
      const errorText = '抱歉，处理您的请求时出现了错误。';
      setResponse(errorText);
      addBotMessage(errorText);
      speakText(errorText);
    } finally {
      setIsProcessing(false);
      setLoading(false);
    }
  };

  // 语音播报
  const speakText = (text) => {
    if (!speechSynthesisRef.current) {
      message.warning('您的浏览器不支持语音播报功能');
      return;
    }

    // 停止当前播报
    speechSynthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-CN';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => {
      setIsSpeaking(false);
      message.error('语音播报失败');
    };

    speechSynthesisRef.current.speak(utterance);
  };

  // 停止语音播报
  const stopSpeaking = () => {
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  return (
    <div style={{ 
      padding: '24px', 
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white'
    }}>
      <Card 
        style={{ 
          width: '100%', 
          maxWidth: '500px',
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          border: 'none'
        }}
        bodyStyle={{ padding: '32px' }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* 机器人头像 */}
          <Avatar 
            size={80} 
            icon={<RobotOutlined />} 
            style={{ 
              backgroundColor: '#1890ff',
              margin: '0 auto'
            }} 
          />

          <Title level={3} style={{ margin: 0, color: '#333' }}>
            AI语音助手
          </Title>

          {/* 状态显示 */}
          {isListening && (
            <div>
              <Text type="secondary">正在倾听...</Text>
              <Progress 
                percent={volume} 
                showInfo={false} 
                strokeColor="#1890ff"
                style={{ marginTop: 8 }}
              />
            </div>
          )}

          {isProcessing && (
            <Text type="secondary">
              <SoundOutlined spin /> 正在处理您的请求...
            </Text>
          )}

          {isSpeaking && (
            <Text type="secondary">
              <SoundOutlined /> 正在为您播报回复...
            </Text>
          )}

          {/* 识别的文本 */}
          {transcript && (
            <Card size="small" style={{ background: '#f0f8ff' }}>
              <Text strong>您说的是：</Text>
              <Paragraph style={{ margin: '8px 0 0 0' }}>
                "{transcript}"
              </Paragraph>
            </Card>
          )}

          {/* AI回复 */}
          {response && (
            <Card size="small" style={{ background: '#f6ffed' }}>
              <Text strong>AI回复：</Text>
              <Paragraph style={{ margin: '8px 0 0 0' }}>
                {response}
              </Paragraph>
            </Card>
          )}

          {/* 控制按钮 */}
          <Space size="large">
            {!isListening ? (
              <Button
                type="primary"
                size="large"
                icon={<CustomerServiceOutlined />}
                onClick={startListening}
                disabled={isProcessing}
                style={{ 
                  width: '120px',
                  height: '50px',
                  borderRadius: '25px'
                }}
              >
                开始说话
              </Button>
            ) : (
              <Button
                danger
                size="large"
                icon={<StopOutlined />}
                onClick={stopListening}
                style={{ 
                  width: '120px',
                  height: '50px',
                  borderRadius: '25px'
                }}
              >
                停止录音
              </Button>
            )}

            {isSpeaking && (
              <Button
                size="large"
                icon={<StopOutlined />}
                onClick={stopSpeaking}
                style={{ 
                  width: '120px',
                  height: '50px',
                  borderRadius: '25px'
                }}
              >
                停止播报
              </Button>
            )}

            {response && !isSpeaking && (
              <Button
                size="large"
                icon={<PlayCircleOutlined />}
                onClick={() => speakText(response)}
                style={{ 
                  width: '120px',
                  height: '50px',
                  borderRadius: '25px'
                }}
              >
                重新播报
              </Button>
            )}
          </Space>

          <Text type="secondary" style={{ fontSize: '12px' }}>
            点击"开始说话"按钮，然后说出您的需求
          </Text>
        </Space>
      </Card>
    </div>
  );
};

export default VoiceChat;