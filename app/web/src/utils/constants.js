// API相关常量
export const API_ENDPOINTS = {
  TASKS: '/v1/tasks/',
  TOOLS: '/v1/mcp/tools',
  SYSTEM: {
    INFO: '/v1/system/info',
    CPU: '/v1/system/cpu',
    MEMORY: '/v1/system/memory',
    DISK: '/v1/system/disk',
    NETWORK: '/v1/system/network',
    PROCESSES: '/v1/system/processes',
    HEALTH: '/v1/system/health',
  }
};

// 系统状态常量
export const SYSTEM_STATUS = {
  NORMAL: 'normal',
  WARNING: 'warning',
  ERROR: 'error'
};