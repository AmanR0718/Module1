import React, { useEffect, useState } from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { ActivityIndicator, View } from "react-native";

import LoginScreen from "../screens/LoginScreen";
import HomeScreen from "./screens/HomeScreen";

import { autoLogin } from "../services/api"; // ensures session restore

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  const [initialRoute, setInitialRoute] = useState(null);

  useEffect(() => {
    const restoreSession = async () => {
      try {
        const user = await autoLogin();
        setInitialRoute(user ? "Home" : "Login");
      } catch {
        setInitialRoute("Login");
      }
    };
    restoreSession();
  }, []);

  if (!initialRoute) {
    return (
      <View
        style={{
          flex: 1,
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#198A48",
        }}
      >
        <ActivityIndicator color="#fff" size="large" />
      </View>
    );
  }

  return (
    <Stack.Navigator
      initialRouteName={initialRoute}
      screenOptions={{
        headerShown: false,
        animation: "slide_from_right",
      }}
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Home" component={HomeScreen} /> {/* ✅ Required */}
    </Stack.Navigator>
  );
}
