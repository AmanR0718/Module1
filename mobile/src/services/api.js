import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://192.168.1.100:8000';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    async (config) => {
        const token = await SecureStore.getItemAsync('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Token expired, try to refresh
            await SecureStore.deleteItemAsync('access_token');
            // Redirect to login
        }
        return Promise.reject(error);
    }
);

// Auth APIs
export const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });

    // Save tokens
    await SecureStore.setItemAsync('access_token', response.data.access_token);
    await SecureStore.setItemAsync('refresh_token', response.data.refresh_token);

    return response.data;
};

export const logout = async () => {
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('refresh_token');
};

export const getCurrentUser = async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
};

// Farmer APIs
export const syncFarmers = async (farmersData) => {
    const response = await api.post('/api/farmers/sync/batch', {
        farmers: farmersData
    });
    return response.data;
};

export const getFarmer = async (farmerId) => {
    const response = await api.get(`/api/farmers/${farmerId}`);
    return response.data;
};

export const searchFarmerByPhone = async (phone) => {
    const response = await api.get(`/api/farmers/search/by-phone?phone=${phone}`);
    return response.data;
};

// Chiefs APIs
export const getProvinces = async () => {
    const response = await api.get('/api/chiefs/provinces');
    return response.data.provinces;
};

export const getDistricts = async (province) => {
    const response = await api.get(`/api/chiefs/districts?province=${province}`);
    return response.data.districts;
};

export const getChiefs = async (province, district) => {
    const response = await api.get(`/api/chiefs/?province=${province}&district=${district}`);
    return response.data;
};

// File upload
export const uploadDocument = async (farmerId, file, documentType) => {
    const formData = new FormData();
    formData.append('file', {
        uri: file.uri,
        name: file.fileName || 'document.jpg',
        type: file.mimeType || 'image/jpeg',
    });

    const response = await api.post(
        `/api/farmers/${farmerId}/upload-document?document_type=${documentType}`,
        formData,
        {
            headers: { 'Content-Type': 'multipart/form-data' },
        }
    );

    return response.data;
};

export default api;
