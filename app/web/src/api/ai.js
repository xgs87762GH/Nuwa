import api from './config';

// Get all AI service providers
export const getAllProviders = async () => {
  return await api.get('/v1/ai/services');
};

// Get current active AI provider
export const getCurrentProvider = async () => {
  return await api.get('/v1/ai/provider/current');
};

// Set default AI provider
export const setDefaultProvider = async (providerType) => {
  return await api.post(`/v1/ai/set_default/${providerType}`);
};

// Get models for specific provider
export const getProviderModels = async (providerType) => {
  return await api.get(`/v1/ai/provider/models/${providerType}`);
};