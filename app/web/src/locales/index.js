// Language configuration index
import zhTranslations from './zh.js';
import enTranslations from './en.js';

// 支持的语言列表
export const supportedLanguages = [
  {
    code: 'zh',
    name: 'Chinese',
    nativeName: '中文',
    flag: '🇨🇳'
  },
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    flag: '🇺🇸'
  }
];

// 语言包映射
export const translations = {
  zh: zhTranslations,
  en: enTranslations
};

// 默认语言
export const defaultLanguage = 'zh';

// 获取浏览器首选语言
export const getBrowserLanguage = () => {
  const browserLang = navigator.language.split('-')[0];
  return supportedLanguages.find(lang => lang.code === browserLang)?.code || defaultLanguage;
};

// 获取语言显示名称
export const getLanguageDisplayName = (code, currentLanguage = 'zh') => {
  const lang = supportedLanguages.find(l => l.code === code);
  if (!lang) return code;
  
  return currentLanguage === 'zh' ? lang.nativeName : lang.name;
};

export default translations;