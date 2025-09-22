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

// 任务状态常量
export const TASK_STATUS = {
  PENDING: 'pending',
  SCHEDULED: 'scheduled',
  RUNNING: 'running',
  SUCCESS: 'success',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
  PAUSED: 'paused',
  TIMEOUT: 'timeout'
};

// 任务状态标签映射 (这里使用状态键作为国际化 ID，在实际使用时通过 t 函数翻译)
export const TASK_STATUS_LABELS = {
  [TASK_STATUS.PENDING]: 'tasks.status.pending',
  [TASK_STATUS.SCHEDULED]: 'tasks.status.scheduled',
  [TASK_STATUS.RUNNING]: 'tasks.status.running',
  [TASK_STATUS.SUCCESS]: 'tasks.status.success',
  [TASK_STATUS.FAILED]: 'tasks.status.failed',
  [TASK_STATUS.CANCELLED]: 'tasks.status.cancelled',
  [TASK_STATUS.PAUSED]: 'tasks.status.paused',
  [TASK_STATUS.TIMEOUT]: 'tasks.status.timeout'
};

// 任务状态颜色映射
export const TASK_STATUS_COLORS = {
  [TASK_STATUS.PENDING]: 'default',
  [TASK_STATUS.SCHEDULED]: 'blue',
  [TASK_STATUS.RUNNING]: 'processing',
  [TASK_STATUS.SUCCESS]: 'success',
  [TASK_STATUS.FAILED]: 'error',
  [TASK_STATUS.CANCELLED]: 'default',
  [TASK_STATUS.PAUSED]: 'warning',
  [TASK_STATUS.TIMEOUT]: 'error'
};