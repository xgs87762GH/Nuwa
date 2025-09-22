import React, { createContext, useContext, useState, useEffect } from 'react';
import { translations, supportedLanguages, defaultLanguage, getBrowserLanguage } from '../locales';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState(defaultLanguage);

  // 从localStorage加载语言设置，如果没有则使用浏览器语言
  useEffect(() => {
    const savedLanguage = localStorage.getItem('nuwa-language');
    if (savedLanguage && translations[savedLanguage]) {
      setCurrentLanguage(savedLanguage);
    } else {
      const browserLanguage = getBrowserLanguage();
      setCurrentLanguage(browserLanguage);
      localStorage.setItem('nuwa-language', browserLanguage);
    }
  }, []);

  // 切换语言
  const switchLanguage = (language) => {
    if (translations[language]) {
      setCurrentLanguage(language);
      localStorage.setItem('nuwa-language', language);
    } else {
      console.warn(`Language '${language}' is not supported`);
    }
  };

  // 获取翻译文本，支持插值
  const t = (key, params = {}) => {
    const keys = key.split('.');
    let text = translations[currentLanguage];
    
    for (const k of keys) {
      text = text?.[k];
    }
    
    if (typeof text !== 'string') {
      console.warn(`Translation key '${key}' not found for language '${currentLanguage}'`);
      return key;
    }

    // 支持参数插值，如 {min}, {max} 等
    return text.replace(/\{(\w+)\}/g, (match, param) => {
      return params[param] !== undefined ? params[param] : match;
    });
  };

  // 检查某个翻译键是否存在
  const hasTranslation = (key) => {
    const keys = key.split('.');
    let text = translations[currentLanguage];
    
    for (const k of keys) {
      text = text?.[k];
    }
    
    return typeof text === 'string';
  };

  const value = {
    currentLanguage,
    switchLanguage,
    t,
    hasTranslation,
    availableLanguages: supportedLanguages,
    isRTL: false // 当前支持的语言都是LTR，如果添加阿拉伯语等RTL语言需要更新
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};