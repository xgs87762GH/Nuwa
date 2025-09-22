import api from './config';

// Get all available tools
export const getTools = async () => {
  return await api.get('/v1/mcp/tools');
};

// Get tool details
export const getToolDetails = async (toolId) => {
  return await api.get(`/v1/mcp/tools/${toolId}`);
};

// Get tools statistics
export const getToolsStatistics = async () => {
  return await api.get('/v1/mcp/tools/stats');  
};