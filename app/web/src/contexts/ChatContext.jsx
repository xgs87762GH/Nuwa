import React, { createContext, useContext, useReducer, useEffect } from 'react';

// 聊天状态管理
const ChatContext = createContext();

// 初始状态
const initialState = {
  messages: [
    {
      id: 1,
      type: 'bot',
      content: '您好！我是您的AI助手，有什么可以帮您的吗？',
      timestamp: new Date()
    }
  ],
  isLoading: false,
  isConnected: true,
  chatHistory: [],
  currentSession: null,
  aiConfig: {
    serviceId: null,
    modelId: null,
    settings: {
      temperature: 0.7,
      maxTokens: 2048,
      stream: false
    }
  }
};

// Action 类型
const ActionTypes = {
  ADD_MESSAGE: 'ADD_MESSAGE',
  SET_LOADING: 'SET_LOADING',
  SET_CONNECTED: 'SET_CONNECTED',
  CLEAR_MESSAGES: 'CLEAR_MESSAGES',
  LOAD_HISTORY: 'LOAD_HISTORY',
  START_SESSION: 'START_SESSION',
  END_SESSION: 'END_SESSION',
  UPDATE_AI_CONFIG: 'UPDATE_AI_CONFIG'
};

// Reducer
const chatReducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.ADD_MESSAGE:
      const newMessages = [...state.messages, action.payload];
      // 保存到本地存储
      localStorage.setItem('chat_messages', JSON.stringify(newMessages));
      return {
        ...state,
        messages: newMessages
      };

    case ActionTypes.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };

    case ActionTypes.SET_CONNECTED:
      return {
        ...state,
        isConnected: action.payload
      };

    case ActionTypes.CLEAR_MESSAGES:
      localStorage.removeItem('chat_messages');
      return {
        ...state,
        messages: [initialState.messages[0]] // 保留欢迎消息
      };

    case ActionTypes.LOAD_HISTORY:
      // 确保从localStorage加载的消息中的timestamp是Date对象
      const messagesWithValidTimestamp = action.payload.map(msg => ({
        ...msg,
        timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
      }));
      return {
        ...state,
        messages: messagesWithValidTimestamp
      };

    case ActionTypes.START_SESSION:
      const sessionId = Date.now().toString();
      return {
        ...state,
        currentSession: {
          id: sessionId,
          startTime: new Date(),
          messageCount: 0
        }
      };

    case ActionTypes.END_SESSION:
      if (state.currentSession) {
        const session = {
          ...state.currentSession,
          endTime: new Date(),
          messageCount: state.messages.length
        };
        
        // 保存会话历史
        const history = JSON.parse(localStorage.getItem('chat_history') || '[]');
        history.push(session);
        localStorage.setItem('chat_history', JSON.stringify(history));
      }
      
      return {
        ...state,
        currentSession: null
      };

    case ActionTypes.UPDATE_AI_CONFIG:
      return {
        ...state,
        aiConfig: {
          ...state.aiConfig,
          ...action.payload
        }
      };

    default:
      return state;
  }
};

// 聊天上下文提供者
export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // 从本地存储加载历史消息
  useEffect(() => {
    const savedMessages = localStorage.getItem('chat_messages');
    if (savedMessages) {
      try {
        const messages = JSON.parse(savedMessages);
        // 验证消息格式是否正确
        if (Array.isArray(messages)) {
          dispatch({ type: ActionTypes.LOAD_HISTORY, payload: messages });
        } else {
          console.warn('无效的聊天记录格式，将清除本地存储');
          localStorage.removeItem('chat_messages');
        }
      } catch (error) {
        console.error('加载聊天历史失败:', error);
        // 清除损坏的数据
        localStorage.removeItem('chat_messages');
      }
    }
  }, []);

  // 添加消息
  const addMessage = (message) => {
    const messageWithId = {
      ...message,
      id: Date.now() + Math.random(),
      timestamp: new Date()
    };
    dispatch({ type: ActionTypes.ADD_MESSAGE, payload: messageWithId });
    return messageWithId;
  };

  // 添加用户消息
  const addUserMessage = (content) => {
    return addMessage({
      type: 'user',
      content
    });
  };

  // 添加机器人消息
  const addBotMessage = (content, data = null) => {
    return addMessage({
      type: 'bot',
      content,
      data
    });
  };

  // 设置加载状态
  const setLoading = (loading) => {
    dispatch({ type: ActionTypes.SET_LOADING, payload: loading });
  };

  // 设置连接状态
  const setConnected = (connected) => {
    dispatch({ type: ActionTypes.SET_CONNECTED, payload: connected });
  };

  // 清空消息
  const clearMessages = () => {
    dispatch({ type: ActionTypes.CLEAR_MESSAGES });
  };

  // 开始新会话
  const startSession = () => {
    dispatch({ type: ActionTypes.START_SESSION });
  };

  // 结束会话
  const endSession = () => {
    dispatch({ type: ActionTypes.END_SESSION });
  };

  // 获取聊天统计
  const getChatStats = () => {
    const userMessages = state.messages.filter(msg => msg.type === 'user');
    const botMessages = state.messages.filter(msg => msg.type === 'bot');
    
    return {
      totalMessages: state.messages.length,
      userMessages: userMessages.length,
      botMessages: botMessages.length,
      currentSession: state.currentSession
    };
  };

  // 更新AI配置
  const updateAIConfig = (config) => {
    dispatch({ type: ActionTypes.UPDATE_AI_CONFIG, payload: config });
  };

  const value = {
    // 状态
    ...state,
    
    // 操作方法
    addMessage,
    addUserMessage,
    addBotMessage,
    setLoading,
    setConnected,
    clearMessages,
    startSession,
    endSession,
    getChatStats,
    updateAIConfig
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

// 使用聊天上下文的 Hook
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export default ChatContext;