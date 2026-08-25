import axios from 'axios';

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api').replace(/\/$/, '');

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const requestWithRetry = async (fn, retries = 2, delayMs = 1500) => {
    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            if (attempt < retries && (!error.response || error.response.status >= 500)) {
                await delay(delayMs);
                continue;
            }
            if (error.response && error.response.data) {
                throw error.response.data;
            }
            throw new Error('Server connection error. The server may be waking up, please click Retry.');
        }
    }
};

export const checkHealth = async () => {
    return requestWithRetry(() => axios.get(`${API_BASE_URL}/health`).then(res => res.data));
};

export const uploadResume = async (file) => {
    const formData = new FormData();
    formData.append('resume', file);
    
    return requestWithRetry(() => axios.post(`${API_BASE_URL}/resumes/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data));
};

export const parseResume = async (resumeId) => {
    return requestWithRetry(() => axios.post(`${API_BASE_URL}/resumes/${resumeId}/parse`).then(res => res.data));
};

export const extractSkills = async (resumeId) => {
    return requestWithRetry(() => axios.post(`${API_BASE_URL}/resumes/${resumeId}/extract-skills`).then(res => res.data));
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
