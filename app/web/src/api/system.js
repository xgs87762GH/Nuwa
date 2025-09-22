import api from './config';

// Get system basic information
export const getSystemInfo = async () => {
  return await api.get('/v1/system/info');
};

// Get system health status
export const getSystemHealth = async () => {
  return await api.get('/v1/system/health');
};

// Get CPU information
export const getCpuInfo = async () => {
  return await api.get('/v1/system/cpu');
};

// Get memory information
export const getMemoryInfo = async () => {
  return await api.get('/v1/system/memory');
};

// Get disk information
export const getDiskInfo = async () => {
  return await api.get('/v1/system/disk');
};

// Get network information
export const getNetworkInfo = async () => {
  return await api.get('/v1/system/network');
};

// Get process information
export const getProcessInfo = async (limit = 10) => {
  return await api.get(`/v1/system/processes?limit=${limit}`);
};