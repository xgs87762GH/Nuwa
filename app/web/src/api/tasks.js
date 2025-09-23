import api from './config';

// Create AI task
export const createTask = async (userInput, options = {}) => {
  return await api.post('/v1/tasks/', {
    user_input: userInput,
    ...options
  }, {
    timeout: options.timeout || 60000
  });
};

// Get tasks list
export const getTasksList = async (params = {}) => {
  try {
    const response = await api.get('/v1/tasks', { params });
    return response;
  } catch (error) {
    console.error('Get tasks list error:', error);
    throw error;
  }
};

// Delete task
export const deleteTask = async (taskId) => {
  try {
    const response = await api.delete(`/v1/tasks/${taskId}`);
    return response;
  } catch (error) {
    console.error('Delete task error:', error);
    throw error;
  }
};