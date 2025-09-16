import api from './config';

// 获取系统基本信息
export const getSystemInfo = async () => {
  return await api.get('/v1/system/info');
};

// 获取CPU信息
export const getCpuInfo = async () => {
  return await api.get('/v1/system/cpu');
};

// 获取内存信息
export const getMemoryInfo = async () => {
  return await api.get('/v1/system/memory');
};

// 获取磁盘信息
export const getDiskInfo = async () => {
  return await api.get('/v1/system/disk');
};

// 获取网络信息
export const getNetworkInfo = async () => {
  return await api.get('/v1/system/network');
};

// 获取进程信息
export const getProcessInfo = async (limit = 10) => {
  return await api.get(`/v1/system/processes?limit=${limit}`);
};

// 系统健康检查
export const getSystemHealth = async () => {
  return await api.get('/v1/system/health');
};