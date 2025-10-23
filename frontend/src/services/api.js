import axios from 'axios';

// Determine the base URL based on environment
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

console.log('API Base URL:', API_BASE_URL);

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes - PDF processing can take time
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log('📤 API Request:', config.method.toUpperCase(), config.url);
    console.log('📤 Base URL:', config.baseURL);
    console.log('📤 Full URL:', `${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging and error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    console.log('Response data:', response.data);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      console.error('Error response headers:', error.response.headers);
    } else if (error.request) {
      // Request was made but no response received
      console.error('No response received:', error.request);
    } else {
      // Something else happened
      console.error('Error message:', error.message);
    }
    
    return Promise.reject(error);
  }
);

/**
 * Upload a PDF file to the backend for processing
 * @param {File} file - The PDF file to upload
 * @returns {Promise} - Response containing success status and document info
 */
export const uploadDocument = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    console.log('📤 Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);

    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log('Upload successful:', response.data);
    return response.data;
    
  } catch (error) {
    console.error('Upload failed:', error);
    
    // Extract meaningful error message
    let errorMessage = 'Upload failed';
    
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    throw new Error(errorMessage);
  }
};

/**
 * Query the RAG system with a question
 * @param {string} question - User's question
 * @returns {Promise} - Response containing answer and sources
 */
export const queryDocuments = async (question) => {
  try {
    const response = await apiClient.post('/query', { question });
    return response.data;
  } catch (error) {
    console.error('Query failed:', error);
    throw error;
  }
};

/**
 * Health check endpoint
 * @returns {Promise} - Response containing health status
 */
export const healthCheck = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * Get list of all documents in the knowledge base
 * @returns {Promise} - Response containing list of documents
 */
export const listDocuments = async () => {
  try {
    const response = await apiClient.get('/documents');
    return response.data;
  } catch (error) {
    console.error('Failed to list documents:', error);
    throw error;
  }
};


export default apiClient;