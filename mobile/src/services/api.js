// =============================================
// File: mobile/src/services/api.js
// Zambian Farmer System – Mobile API Service
// =============================================

import axios from "axios";
import * as SecureStore from "expo-secure-store";
import * as Network from "expo-network";

const API_BASE_URL =
    process.env.EXPO_PUBLIC_API_URL || "http://10.169.131.102:8000";

// Axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: { "Content-Type": "application/json" },
});

// ============================================================
// 🔹 AUTH TOKEN MANAGEMENT
// ============================================================

// Add token before requests
api.interceptors.request.use(
    async (config) => {
        const token = await SecureStore.getItemAsync("access_token");
        if (token) config.headers.Authorization = `Bearer ${token}`;
        return config;
    },
    (error) => Promise.reject(error)
);

// Handle expired tokens
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            const newToken = await refreshAccessToken();
            if (newToken) {
                error.config.headers.Authorization = `Bearer ${newToken}`;
                return api.request(error.config);
            }
            await logout();
        }
        return Promise.reject(error);
    }
);

// ============================================================
// 🔹 AUTHENTICATION
// ============================================================
export const login = async (email, password) => {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const response = await api.post("/api/auth/login", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });

    await SecureStore.setItemAsync("access_token", response.data.access_token);
    await SecureStore.setItemAsync("refresh_token", response.data.refresh_token);

    return response.data;
};

export const logout = async () => {
    await SecureStore.deleteItemAsync("access_token");
    await SecureStore.deleteItemAsync("refresh_token");
};

export const getCurrentUser = async () => {
    const response = await api.get("/api/auth/me");
    return response.data;
};

const refreshAccessToken = async () => {
    try {
        const refreshToken = await SecureStore.getItemAsync("refresh_token");
        if (!refreshToken) return null;

        const response = await api.post("/api/auth/refresh", {
            refresh_token: refreshToken,
        });

        const newAccessToken = response.data.access_token;
        await SecureStore.setItemAsync("access_token", newAccessToken);

        console.log("🔁 Access token refreshed successfully.");
        return newAccessToken;
    } catch (error) {
        console.error("❌ Token refresh failed:", error);
        return null;
    }
};

// ============================================================
// 🔹 FARMER APIs
// ============================================================
export const registerFarmer = async (farmerData) => {
    const response = await api.post("/api/farmers/", farmerData);
    return response.data;
};

export const getFarmer = async (farmerId) => {
    const response = await api.get(`/api/farmers/${farmerId}`);
    return response.data;
};

export const searchFarmerByPhone = async (phone) => {
    const response = await api.get(`/api/farmers/?phone=${encodeURIComponent(phone)}`);
    if (response.data && response.data.length > 0) return response.data[0];
    throw new Error("Farmer not found");
};

// Batch sync offline farmers to backend
export const syncFarmers = async (farmersData) => {
    const response = await api.post("/api/sync/batch", { farmers: farmersData });
    return response.data;
};

// Farmer stats for dashboard
export const getFarmerStats = async () => {
    const response = await api.get("/api/farmers/stats");
    return response.data;
};

// ============================================================
// 🔹 CHIEFS & LOCATION APIs
// ============================================================
export const getProvinces = async () => {
    const response = await api.get("/api/chiefs/provinces");
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

// ============================================================
// 🔹 FILE UPLOADS (Farmer Photo / ID)
// ============================================================
export const uploadDocument = async (farmerId, fileUri, documentType) => {
    const formData = new FormData();
    formData.append("file", {
        uri: fileUri,
        name: fileUri.split("/").pop() || "document.jpg",
        type: "image/jpeg",
    });

    const response = await api.post(
        `/api/farmers/${farmerId}/upload-document?document_type=${documentType}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
    );

    return response.data;
};

// ============================================================
// 🔹 NETWORK HELPER
// ============================================================
export const ensureOnline = async () => {
    const state = await Network.getNetworkStateAsync();
    if (!state.isConnected || !state.isInternetReachable) {
        throw new Error("No internet connection");
    }
};

// Export all
export default api;
