import React, { createContext, useContext, useState, useEffect } from 'react';

// 语言包定义
const translations = {
  zh: {
    // AI Chat Interface
    aiChat: {
      title: 'AI智能助手',
      textMode: '文字模式',
      voiceMode: '语音模式',
      startSpeaking: '🎤 开始说话',
      stopRecording: '⏹️ 停止录音',
      stopSpeaking: '停止播报',
      listening: '🎤 正在倾听您的声音...',
      processing: 'AI正在思考中...',
      recognized: '识别到',
      inputPlaceholder: '输入您的消息... (Shift+Enter 换行，Enter 发送)',
      send: '发送',
      selectModel: '选择模型',
      currentModel: '当前模型',
      noModelsAvailable: '暂无可用模型'
    },
    // System Settings
    system: {
      title: '系统设置',
      aiProvider: 'AI提供商',
      currentProvider: '当前提供商',
      selectProvider: '选择提供商',
      language: '语言',
      save: '保存',
      cancel: '取消'
    },
    // Settings Modal
    settings: {
      title: '设置',
      aiSettings: 'AI设置',
      systemSettings: '系统设置',
      currentLanguage: '当前语言',
      themeSettings: '主题设置',
      currentTheme: '当前主题',
      themeChanged: '主题已切换',
      notSet: '未设置',
      available: '可用',
      unavailable: '不可用',
      refresh: '刷新',
      selectProvider: '选择AI提供商',
      themes: {
        default: '默认',
        ocean: '海洋',
        sunset: '夕阳',
        forest: '森林',
        purple: '紫色'
      }
    },
    // Navigation
    navigation: {
      home: '首页',
      tasks: '任务管理',
      tools: '工具管理',
      system: '系统设置',
      settings: '设置'
    },
    // Common
    common: {
      loading: '加载中...',
      success: '成功',
      error: '错误',
      warning: '警告',
      confirm: '确认',
      language: '语言',
      platform: '智能AI平台'
    },
    // Messages
    messages: {
      sendSuccess: '消息发送成功',
      sendFailed: '发送消息失败',
      providerSwitchSuccess: 'AI提供商切换成功',
      loadProvidersFailed: '加载AI提供商列表失败',
      noSpeechSupport: '您的浏览器不支持语音功能',
      speechRecognitionFailed: '语音识别失败，请重试',
      speechSynthesisFailed: '语音播报失败'
    }
  },
  en: {
    // AI Chat Interface
    aiChat: {
      title: 'AI Assistant',
      textMode: 'Text Mode',
      voiceMode: 'Voice Mode',
      startSpeaking: '🎤 Start Speaking',
      stopRecording: '⏹️ Stop Recording',
      stopSpeaking: 'Stop Speaking',
      listening: '🎤 Listening to your voice...',
      processing: 'AI is thinking...',
      recognized: 'Recognized',
      inputPlaceholder: 'Enter your message... (Shift+Enter for new line, Enter to send)',
      send: 'Send',
      selectModel: 'Select Model',
      currentModel: 'Current Model',
      noModelsAvailable: 'No models available'
    },
    // System Settings
    system: {
      title: 'System Settings',
      aiProvider: 'AI Provider',
      currentProvider: 'Current Provider',
      selectProvider: 'Select Provider',
      language: 'Language',
      save: 'Save',
      cancel: 'Cancel'
    },
    // Settings Modal
    settings: {
      title: 'Settings',
      aiSettings: 'AI Settings',
      systemSettings: 'System Settings',
      currentLanguage: 'Current Language',
      themeSettings: 'Theme Settings',
      currentTheme: 'Current Theme',
      themeChanged: 'Theme changed successfully',
      notSet: 'Not Set',
      available: 'Available',
      unavailable: 'Unavailable',
      refresh: 'Refresh',
      selectProvider: 'Select AI Provider',
      themes: {
        default: 'Default',
        ocean: 'Ocean',
        sunset: 'Sunset',
        forest: 'Forest',
        purple: 'Purple'
      }
    },
    // Navigation
    navigation: {
      home: 'Home',
      tasks: 'Tasks',
      tools: 'Tools',
      system: 'System',
      settings: 'Settings'
    },
    // Common
    common: {
      loading: 'Loading...',
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      confirm: 'Confirm',
      language: 'Language',
      platform: 'AI Platform'
    },
    // Messages
    messages: {
      sendSuccess: 'Message sent successfully',
      sendFailed: 'Failed to send message',
      providerSwitchSuccess: 'AI provider switched successfully',
      loadProvidersFailed: 'Failed to load AI providers',
      noSpeechSupport: 'Your browser does not support speech features',
      speechRecognitionFailed: 'Speech recognition failed, please try again',
      speechSynthesisFailed: 'Speech synthesis failed'
    }
  }
};

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('zh');

  // 从localStorage加载语言设置
  useEffect(() => {
    const savedLanguage = localStorage.getItem('nuwa-language') || 'zh';
    setCurrentLanguage(savedLanguage);
  }, []);

  // 切换语言
  const switchLanguage = (language) => {
    setCurrentLanguage(language);
    localStorage.setItem('nuwa-language', language);
  };

  // 获取翻译文本
  const t = (key) => {
    const keys = key.split('.');
    let text = translations[currentLanguage];
    
    for (const k of keys) {
      text = text?.[k];
    }
    
    return text || key;
  };

  const value = {
    currentLanguage,
    switchLanguage,
    t,
    availableLanguages: [
      { code: 'zh', name: '中文', nativeName: '中文' },
      { code: 'en', name: 'English', nativeName: 'English' }
    ]
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};