import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

export const checkHealth = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/health`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const uploadResume = async (file) => {
    const formData = new FormData();
    formData.append('resume', file);
    
    try {
        const response = await axios.post(`${API_BASE_URL}/resumes/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : new Error('Network error');
    }
};

export const parseResume = async (resumeId) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/resumes/${resumeId}/parse`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : new Error('Network error');
    }
};

export const extractSkills = async (resumeId) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/resumes/${resumeId}/extract-skills`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : new Error('Network error');
    }
};

export const createJob = async (jobData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/jobs`, jobData);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : new Error('Network error');
    }
};

export const analyzeJob = async (jobId) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/jobs/${jobId}/analyze`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : new Error('Network error');
    }
};

export const matchResumeToJob = async (resumeId, jobId) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/resumes/${resumeId}/jobs/${jobId}/match`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : new Error('Network error');
    }
};
