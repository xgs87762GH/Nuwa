import api from './config';
import { mockAIServices, simulateAPIDelay } from '../utils/mockData';

// 是否使用模拟数据（开发环境）
// const USE_MOCK_DATA = process.env.NODE_ENV === 'development';
const USE_MOCK_DATA = false;

// 获取AI模型服务列表
export const getAIServices = async () => {
  if (USE_MOCK_DATA) {
    await simulateAPIDelay(500);
    return {
      data: {
        providers: mockAIServices.map(service => ({
          type: service.id,
          default_model: service.models[0]?.id || 'unknown',
          models: service.models.map(m => m.id),
          base_url: 'mock_url',
          status: service.status === 'online' ? 'active' : 'inactive',
          initialized_at: new Date().toISOString()
        })),
        total: mockAIServices.length
      }
    };
  }
  return await api.get('/v1/ai/services');
};

// 获取指定提供商的AI模型列表
export const getAIModels = async (providerType) => {
  if (USE_MOCK_DATA) {
    await simulateAPIDelay(300);
    const service = mockAIServices.find(s => s.id === providerType);
    return {
      data: service ? service.models.map(m => m.id) : []
    };
  }
  return await api.get(`/v1/ai/provider/models/${providerType}`);
};

// 设置默认AI提供商
export const setDefaultAIProvider = async (providerType) => {
  return await api.post(`/v1/ai/set_default/${providerType}`);
};

// 获取当前AI提供商
export const getCurrentAIProvider = async () => {
  return await api.get('/v1/ai/provider/current');
};

// 获取AI服务状态（从服务列表中获取）
export const getServiceStatus = async (providerType) => {
  if (USE_MOCK_DATA) {
    await simulateAPIDelay(200);
    const service = mockAIServices.find(s => s.id === providerType);
    return {
      data: {
        status: service ? service.status : 'offline',
        lastCheck: new Date().toISOString(),
        responseTime: Math.floor(Math.random() * 500) + 100
      }
    };
  }
  
  // 通过获取服务列表来检查状态
  try {
    const response = await api.get('/v1/ai/services');
    const provider = response.data?.providers?.find(p => p.type === providerType);
    return {
      data: {
        status: provider ? provider.status : 'inactive',
        lastCheck: provider ? provider.initialized_at : new Date().toISOString(),
        responseTime: Math.floor(Math.random() * 500) + 100
      }
    };
  } catch (error) {
    return {
      data: {
        status: 'offline',
        lastCheck: new Date().toISOString(),
        responseTime: 0
      }
    };
  }
};

// 创建聊天任务（支持模型选择）
export const createChatTask = async (userInput, options = {}) => {
  const payload = {
    user_input: userInput,
    provider_type: options.serviceId,
    model: options.modelId,
    temperature: options.temperature || 0.7,
    max_tokens: options.maxTokens || 2048,
    stream: options.stream || false
  };
  
  return await api.post('/v1/tasks/', payload, {
    timeout: options.timeout || 60000
  });
};

// 获取聊天历史
export const getChatHistory = async (sessionId) => {
  return await api.get(`/v1/chat/history/${sessionId}`);
};

// 删除聊天会话
export const deleteChatSession = async (sessionId) => {
  return await api.delete(`/v1/chat/sessions/${sessionId}`);
};