// Unified API exports
// Import all API modules and re-export them

// All imports must be at the top
import * as ai from './ai';
import * as system from './system';
import * as tasks from './tasks';
import * as tools from './tools';
import * as health from './health';

// Modern exports - re-export modules with consistent naming
export { ai as aiAPI };
export { system as systemAPI };
export { tasks as taskAPI };
export { tools as mcpAPI };
export { health as healthAPI };

// Individual function exports for convenience
export {
  getAllProviders,
  getCurrentProvider,
  setDefaultProvider,
  getProviderModels
} from './ai';

export {
  getSystemInfo,
  getSystemHealth,
  getCpuInfo,
  getMemoryInfo,
  getDiskInfo,
  getNetworkInfo,
  getProcessInfo
} from './system';

export {
  createTask,
  getTasksList
} from './tasks';

export {
  getTools,
  getToolsStatistics,
  getToolDetails
} from './tools';

export {
  checkHealth,
  getRootInfo
} from './health';