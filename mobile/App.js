// mobile/App.js
import React, { useEffect, useState } from "react";
import { View, Text, ActivityIndicator, Alert } from "react-native";
import Constants from "expo-constants";
import { NavigationContainer } from "@react-navigation/native";
import AppNavigator from "./src/navigation/AppNavigator"; // 👈 your full app routes

const API_URL =
  process.env.EXPO_PUBLIC_API_URL || Constants.expoConfig?.extra?.apiUrl;

export default function App() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const testBackend = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        if (data?.status === "healthy") {
          setBackendStatus("healthy");
        } else {
          setBackendStatus("unhealthy");
        }
      } catch (error) {
        console.warn("Backend check failed:", error.message);
        setBackendStatus("unreachable");
      } finally {
        setLoading(false);
      }
    };
    testBackend();
  }, []);

  if (loading) {
    return (
      <View
        style={{
          flex: 1,
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#fff",
        }}
      >
        <ActivityIndicator size="large" color="#198A48" />
        <Text>Checking backend connection...</Text>
      </View>
    );
  }

  if (backendStatus === "unreachable") {
    Alert.alert(
      "Warning",
      "Backend not reachable — some features may not sync."
    );
  }

  return (
    <NavigationContainer>
      <AppNavigator />
    </NavigationContainer>
  );
}
