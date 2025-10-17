// mobile/App.js
import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  Alert,
  StyleSheet,
  ScrollView,
  Platform,
} from "react-native";
import Constants from "expo-constants";

const API_URL =
  process.env.EXPO_PUBLIC_API_URL || Constants.expoConfig?.extra?.apiUrl;

const App = () => {
  const [backendStatus, setBackendStatus] = useState("Not Tested");
  const [loading, setLoading] = useState(false);

  const testBackend = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      setBackendStatus(`✅ ${data.status}`);
      Alert.alert("Success", "Backend Status: " + data.status);
    } catch (error) {
      setBackendStatus("❌ Connection Failed");
      Alert.alert("Error", "Backend connection failed: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView
      contentContainerStyle={styles.container}
      style={{ backgroundColor: "#f5f5f5" }}
    >
      <Text style={styles.title}>🌾 Zambian Farmer System</Text>
      <Text style={styles.subtitle}>
        {Platform.OS === "web" ? "Web Test Version" : "Mobile App Version"}
      </Text>

      <TouchableOpacity
        style={[styles.button, loading && { opacity: 0.6 }]}
        onPress={testBackend}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading ? "Testing..." : "🔗 Test Backend Connection"}
        </Text>
      </TouchableOpacity>

      <View style={styles.card}>
        <Text style={styles.info}>
          <Text style={styles.bold}>Backend URL: </Text>
          {API_URL}
        </Text>
        <Text style={styles.info}>
          <Text style={styles.bold}>Platform: </Text>
          {Platform.OS === "web" ? "Web Browser" : "Expo Mobile"}
        </Text>
        <Text style={styles.info}>
          <Text style={styles.bold}>Status: </Text>
          {backendStatus}
        </Text>
      </View>
    </ScrollView>
  );
};

// ============================================================
// 🔹 STYLES
// ============================================================
const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 50,
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 26,
    fontWeight: "bold",
    color: "#2c3e50",
    marginBottom: 10,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 18,
    color: "#7f8c8d",
    marginBottom: 40,
    textAlign: "center",
  },
  button: {
    backgroundColor: "#198A48",
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 10,
    elevation: 3,
    marginBottom: 20,
  },
  buttonText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 16,
  },
  card: {
    backgroundColor: "#fff",
    padding: 20,
    borderRadius: 10,
    width: "90%",
    borderWidth: 1,
    borderColor: "#ddd",
  },
  info: {
    fontSize: 16,
    color: "#34495e",
    marginBottom: 10,
  },
  bold: {
    fontWeight: "bold",
  },
});

export default App;
