import api from './config';

// 获取所有工具
export const getTools = async () => {
  return await api.get('/v1/mcp/tools');
};

// 获取工具详情
export const getToolDetails = async (toolId) => {
  return await api.get(`/v1/mcp/tools/${toolId}`);
};

// 获取工具数量
export const getToolsStatistics = async () => {
  return await api.get('/v1/mcp/tools/stats');  
}