// 模拟AI服务数据，用于开发测试
export const mockAIServices = [
  {
    id: 'openai',
    name: 'OpenAI',
    provider: 'OpenAI Inc.',
    description: '领先的AI语言模型服务',
    status: 'online',
    models: [
      {
        id: 'gpt-4',
        name: 'GPT-4',
        description: '最先进的大型语言模型，具有卓越的理解和生成能力',
        latest: true,
        maxTokens: 8192,
        supportedFeatures: ['text', 'code', 'analysis']
      },
      {
        id: 'gpt-3.5-turbo',
        name: 'GPT-3.5 Turbo',
        description: '快速响应的对话模型，平衡性能和成本',
        latest: false,
        maxTokens: 4096,
        supportedFeatures: ['text', 'code']
      }
    ]
  },
  {
    id: 'anthropic',
    name: 'Claude',
    provider: 'Anthropic',
    description: '安全可靠的AI助手',
    status: 'online',
    models: [
      {
        id: 'claude-3-opus',
        name: 'Claude 3 Opus',
        description: '最强大的Claude模型，适合复杂任务',
        latest: true,
        maxTokens: 200000,
        supportedFeatures: ['text', 'analysis', 'reasoning']
      },
      {
        id: 'claude-3-sonnet',
        name: 'Claude 3 Sonnet',
        description: '平衡性能和速度的Claude模型',
        latest: false,
        maxTokens: 200000,
        supportedFeatures: ['text', 'analysis']
      }
    ]
  },
  {
    id: 'google',
    name: 'Gemini',
    provider: 'Google',
    description: 'Google的多模态AI模型',
    status: 'online',
    models: [
      {
        id: 'gemini-pro',
        name: 'Gemini Pro',
        description: '强大的多模态模型，支持文本和图像',
        latest: true,
        maxTokens: 32768,
        supportedFeatures: ['text', 'image', 'code']
      }
    ]
  },
  {
    id: 'local',
    name: '本地模型',
    provider: 'Local',
    description: '部署在本地的AI模型',
    status: 'busy',
    models: [
      {
        id: 'llama2-7b',
        name: 'Llama 2 7B',
        description: '开源的7B参数模型',
        latest: false,
        maxTokens: 4096,
        supportedFeatures: ['text']
      },
      {
        id: 'llama2-13b',
        name: 'Llama 2 13B',
        description: '开源的13B参数模型',
        latest: true,
        maxTokens: 4096,
        supportedFeatures: ['text', 'code']
      }
    ]
  }
];

// 模拟API响应的延迟
export const simulateAPIDelay = (ms = 1000) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};