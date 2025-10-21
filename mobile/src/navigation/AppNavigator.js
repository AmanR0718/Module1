// mobile/src/navigation/AppNavigator.js
import React, { useEffect, useState } from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import * as SecureStore from 'expo-secure-store';
import { getCurrentUser } from '../services/api';
import { View, ActivityIndicator, Platform } from 'react-native';

// Screens
import LoginScreen from '../screens/LoginScreen';
import HomeScreen from '../screens/HomeScreen';
import FarmerRegistrationScreen from '../screens/FarmerRegistrationScreen';
import FarmerListScreen from '../screens/FarmerListScreen';
import SearchFarmerScreen from '../screens/SearchFarmerScreen';
import FarmerDetailScreen from '../screens/FarmerDetailScreen';
import InventoryScreen from '../screens/InventoryScreen';   // 🔹 future
import ReportsScreen from '../screens/ReportsScreen';       // 🔹 future
import ForgotPasswordScreen from '../screens/ForgotPasswordScreen'; // ✅ added to handle navigation warning

const Stack = createNativeStackNavigator();

const screenOptions = {
  headerStyle: { backgroundColor: '#198A48' },
  headerTintColor: '#fff',
  headerTitleStyle: { fontWeight: 'bold' },
  headerBackTitleVisible: false,
};

// ✅ SecureStore wrapper to support web fallback
const getToken = async () => {
  try {
    if (Platform.OS === 'web') {
      // Web fallback since SecureStore is native-only
      return localStorage.getItem('access_token');
    }
    return await SecureStore.getItemAsync('access_token');
  } catch (error) {
    console.warn('SecureStore access failed, falling back:', error);
    if (Platform.OS === 'web') return localStorage.getItem('access_token');
    return null;
  }
};

const OperatorStack = () => (
  <Stack.Navigator initialRouteName="Home" screenOptions={screenOptions}>
    <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
    <Stack.Screen
      name="FarmerRegistrationScreen"
      component={FarmerRegistrationScreen}
      options={{ title: 'Register Farmer' }}
    />
    <Stack.Screen
      name="FarmerListScreen"
      component={FarmerListScreen}
      options={{ title: 'All Farmers' }}
    />
    <Stack.Screen
      name="SearchFarmerScreen"
      component={SearchFarmerScreen}
      options={{ title: 'Search Farmer' }}
    />
    <Stack.Screen
      name="FarmerDetail"
      component={FarmerDetailScreen}
      options={{ title: 'Farmer Details' }}
    />
  </Stack.Navigator>
);

const AdminStack = () => (
  <Stack.Navigator initialRouteName="Home" screenOptions={screenOptions}>
    <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
    <Stack.Screen
      name="FarmerListScreen"
      component={FarmerListScreen}
      options={{ title: 'Farmers' }}
    />
    <Stack.Screen
      name="FarmerDetail"
      component={FarmerDetailScreen}
      options={{ title: 'Farmer Details' }}
    />
    <Stack.Screen
      name="InventoryScreen"
      component={InventoryScreen}
      options={{ title: 'Inventory Management' }}
    />
    <Stack.Screen name="ReportsScreen" component={ReportsScreen} options={{ title: 'Reports' }} />
  </Stack.Navigator>
);

const AppNavigator = () => {
  const [initialRoute, setInitialRoute] = useState('Login');
  const [userRole, setUserRole] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuthAndRole = async () => {
      try {
        const token = await getToken();

        if (!token) {
          setInitialRoute('Login');
          setLoading(false);
          return;
        }

        const user = await getCurrentUser();
        if (user?.role) {
          setUserRole(user.role);
          setInitialRoute('Home');
        } else {
          setInitialRoute('Login');
        }
      } catch (error) {
        console.warn('Auth check failed:', error);
        setInitialRoute('Login');
      } finally {
        setLoading(false);
      }
    };

    checkAuthAndRole();
  }, []);

  // 🔄 Loading Spinner (while verifying token)
  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#198A48" />
      </View>
    );
  }

  // 🚀 Main Navigation (NavigationContainer handled in App.js)
  return (
    <Stack.Navigator initialRouteName={initialRoute} screenOptions={screenOptions}>
      <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
      <Stack.Screen
        name="ForgotPassword"
        component={ForgotPasswordScreen}
        options={{ title: 'Forgot Password' }}
      />
      {userRole === 'admin' ? (
        <Stack.Screen name="AdminStack" component={AdminStack} options={{ headerShown: false }} />
      ) : userRole === 'extension_officer' || userRole === 'operator' ? (
        <Stack.Screen
          name="OperatorStack"
          component={OperatorStack}
          options={{ headerShown: false }}
        />
      ) : (
        <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
      )}
    </Stack.Navigator>
  );
};

export default AppNavigator;
