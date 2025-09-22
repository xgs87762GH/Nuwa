import api from './config';

// Basic health check
export const checkHealth = async () => {
  return await api.get('/health');
};

// Get root system information
export const getRootInfo = async () => {
  return await api.get('/');
};