// =============================================
// File: mobile/src/services/api.js
// Zambian Farmer System – Unified API Service
// Cross-platform, Offline-aware, Secure, Future-proof.
// =============================================

import axios from "axios";
import * as Network from "expo-network";
import { Platform } from "react-native";
import * as SecureStore from "expo-secure-store";

// ============================================================
// 🔹 CROSS-PLATFORM STORAGE (SecureStore + localStorage fallback)
// ============================================================

const saveItem = async (key, value) => {
  try {
    if (Platform.OS === "web") {
      localStorage.setItem(key, value);
    } else {
      await SecureStore.setItemAsync(key, value);
    }
  } catch (error) {
    console.error(`Error saving ${key}:`, error);
  }
};

const getItem = async (key) => {
  try {
    if (Platform.OS === "web") {
      return localStorage.getItem(key);
    } else {
      return await SecureStore.getItemAsync(key);
    }
  } catch (error) {
    console.error(`Error retrieving ${key}:`, error);
    return null;
  }
};

const deleteItem = async (key) => {
  try {
    if (Platform.OS === "web") {
      localStorage.removeItem(key);
    } else {
      await SecureStore.deleteItemAsync(key);
    }
  } catch (error) {
    console.error(`Error deleting ${key}:`, error);
  }
};

// ============================================================
// 🔹 BASE URL CONFIGURATION
// ============================================================

const LOCAL_API = "http://127.0.0.1:8000";
const DOCKER_API = "http://10.169.131.102:8000";
const PROD_API = "https://api.zambianfarmer.com";

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "production" ? PROD_API : DOCKER_API);

console.log("🌍 Using API:", API_BASE_URL);

// ============================================================
// 🔹 AXIOS INSTANCE
// ============================================================

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// ============================================================
// 🔹 REQUEST INTERCEPTOR
// ============================================================

api.interceptors.request.use(
  async (config) => {
    const net = await Network.getNetworkStateAsync();
    if (!net.isConnected || !net.isInternetReachable) {
      throw new Error("No internet connection");
    }

    const token = await getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// ============================================================
// 🔹 RESPONSE INTERCEPTOR (Auto-refresh on 401)
// ============================================================

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes("/auth/login")
    ) {
      originalRequest._retry = true;

      const newToken = await refreshAccessToken();
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api.request(originalRequest);
      }

      console.warn("⚠️ Session expired, logging out");
      await logout();
    }

    return Promise.reject(error);
  }
);

// ============================================================
// 🔹 AUTHENTICATION
// ============================================================

export const login = async (email, password) => {
  try {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const response = await api.post("/api/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    const { access_token, refresh_token, user } = response.data;

    if (access_token) await saveItem("access_token", access_token);
    if (refresh_token) await saveItem("refresh_token", refresh_token);
    if (user) await saveItem("user", JSON.stringify(user));

    console.log("✅ Login successful for:", email);
    return response.data;
  } catch (error) {
    console.error("❌ Login error:", error.response?.data || error.message);
    throw new Error(
      error.response?.data?.detail || "Login failed. Please check credentials."
    );
  }
};

export const logout = async () => {
  await deleteItem("access_token");
  await deleteItem("refresh_token");
  await deleteItem("user");
  console.log("👋 Logged out, tokens cleared");
};

export const getCurrentUser = async () => {
  try {
    const res = await api.get("/api/auth/me");
    return res.data;
  } catch (error) {
    console.error("Error fetching current user:", error.message);
    return null;
  }
};

const refreshAccessToken = async () => {
  try {
    const refreshToken = await getItem("refresh_token");
    if (!refreshToken) return null;

    const res = await api.post("/api/auth/refresh", {
      refresh_token: refreshToken,
    });

    const newAccessToken = res.data.access_token;
    await saveItem("access_token", newAccessToken);
    console.log("🔁 Token refreshed successfully");
    return newAccessToken;
  } catch (error) {
    console.error("❌ Token refresh failed:", error.response?.data || error.message);
    return null;
  }
};

// ============================================================
// 🔹 AUTO LOGIN (Session Restore)
// ============================================================

export const autoLogin = async () => {
  try {
    const token = await getItem("access_token");
    if (!token) return null;

    const user = await getCurrentUser();
    if (user) {
      console.log("🔓 Session restored for:", user.email || user.username);
      return user;
    }

    return null;
  } catch (error) {
    console.warn("⚠️ Auto-login failed:", error.message);
    return null;
  }
};

// ============================================================
// 🔹 FARMER APIs
// ============================================================

export const registerFarmer = async (farmerData) => {
  const res = await api.post("/api/farmers/", farmerData);
  return res.data;
};

export const getFarmer = async (id) => {
  const res = await api.get(`/api/farmers/${id}`);
  return res.data;
};

export const searchFarmerByPhone = async (phone) => {
  const res = await api.get(`/api/farmers/?phone=${encodeURIComponent(phone)}`);
  return res.data.length ? res.data[0] : null;
};

export const syncFarmers = async (farmersData) => {
  const res = await api.post("/api/sync/batch", { farmers: farmersData });
  return res.data;
};

export const getFarmerStats = async () => {
  const res = await api.get("/api/farmers/stats");
  return res.data;
};

// ============================================================
// 🔹 CHIEFS & LOCATION APIs
// ============================================================

export const getProvinces = async () => {
  const res = await api.get("/api/chiefs/provinces");
  return res.data.provinces;
};

export const getDistricts = async (province) => {
  const res = await api.get(`/api/chiefs/districts?province=${province}`);
  return res.data.districts;
};

export const getChiefs = async (province, district) => {
  const res = await api.get(`/api/chiefs/?province=${province}&district=${district}`);
  return res.data;
};

// ============================================================
// 🔹 DOCUMENT UPLOAD (Farmer Photos / IDs)
// ============================================================

export const uploadDocument = async (farmerId, fileUri, documentType) => {
  const formData = new FormData();
  formData.append("file", {
    uri: fileUri,
    name: fileUri.split("/").pop() || "document.jpg",
    type: "image/jpeg",
  });

  const res = await api.post(
    `/api/farmers/${farmerId}/upload-document?document_type=${documentType}`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );

  return res.data;
};

// ============================================================
// 🔹 CONNECTIVITY CHECKER
// ============================================================

export const ensureOnline = async () => {
  const net = await Network.getNetworkStateAsync();
  if (!net.isConnected || !net.isInternetReachable) {
    throw new Error("No internet connection detected.");
  }
};

export default api;
