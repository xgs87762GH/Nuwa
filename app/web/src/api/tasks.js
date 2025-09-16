import api from './config';

// 创建任务
export const createTask = async (userInput, timeout = 60000) => {
  return await api.post('/v1/tasks/', 
    { user_input: userInput },
    { timeout: timeout }
  );
};