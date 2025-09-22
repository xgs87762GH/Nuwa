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

// Get tasks list (mock interface, needs backend implementation)
export const getTasksList = async (params = {}) => {
  try {
    // Since there's no list interface in the API docs, using mock data here
    // Should call real API endpoint in actual usage
    const mockData = {
      success: true,
      message: "Success",
      data: {
        page: params.page || 1,
        page_size: params.page_size || 10,
        total: 12,
        tasks: [] // Should be real data from server
      }
    };
    
    return { data: mockData };
  } catch (error) {
    console.error('Get tasks list error:', error);
    throw error;
  }
};