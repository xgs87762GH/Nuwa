import api from './config';

// 创建任务
export const createTask = async (userInput) => {
  return await api.post('/v1/tasks/', { user_input: userInput });
};