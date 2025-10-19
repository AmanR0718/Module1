import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import * as SecureStore from 'expo-secure-store';
import { getCurrentUser } from '../services/api';

// Screens
import LoginScreen from '../screens/LoginScreen';
import HomeScreen from '../screens/HomeScreen';
import FarmerRegistrationScreen from '../screens/FarmerRegistrationScreen';
import FarmerListScreen from '../screens/FarmerListScreen';
import SearchFarmerScreen from '../screens/SearchFarmerScreen';
import FarmerDetailScreen from '../screens/FarmerDetailScreen';
import InventoryScreen from '../screens/InventoryScreen';   // 🔹 future
import ReportsScreen from '../screens/ReportsScreen';       // 🔹 future

const Stack = createNativeStackNavigator();

/**
 * Stack for field operators (mobile data collectors)
 */
const OperatorStack = () => (
    <Stack.Navigator
        initialRouteName="Home"
        screenOptions={screenOptions}
    >
        <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
        <Stack.Screen name="FarmerRegistrationScreen" component={FarmerRegistrationScreen} options={{ title: 'Register Farmer' }} />
        <Stack.Screen name="FarmerListScreen" component={FarmerListScreen} options={{ title: 'All Farmers' }} />
        <Stack.Screen name="SearchFarmerScreen" component={SearchFarmerScreen} options={{ title: 'Search Farmer' }} />
        <Stack.Screen name="FarmerDetail" component={FarmerDetailScreen} options={{ title: 'Farmer Details' }} />
    </Stack.Navigator>
);

/**
 * Stack for admin users (web or mobile supervisors)
 */
const AdminStack = () => (
    <Stack.Navigator
        initialRouteName="Home"
        screenOptions={screenOptions}
    >
        <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
        <Stack.Screen name="FarmerListScreen" component={FarmerListScreen} options={{ title: 'Farmers' }} />
        <Stack.Screen name="FarmerDetail" component={FarmerDetailScreen} options={{ title: 'Farmer Details' }} />
        <Stack.Screen name="InventoryScreen" component={InventoryScreen} options={{ title: 'Inventory Management' }} />
        <Stack.Screen name="ReportsScreen" component={ReportsScreen} options={{ title: 'Reports' }} />
    </Stack.Navigator>
);

const screenOptions = {
    headerStyle: { backgroundColor: '#198A48' },
    headerTintColor: '#fff',
    headerTitleStyle: { fontWeight: 'bold' },
    headerBackTitleVisible: false,
};

/**
 * Main Navigator with role-based routing
 */
const AppNavigator = () => {
    const [initialRoute, setInitialRoute] = useState('Login');
    const [userRole, setUserRole] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuthAndRole = async () => {
            try {
                const token = await SecureStore.getItemAsync('access_token');
                if (!token) {
                    setInitialRoute('Login');
                    setLoading(false);
                    return;
                }

                const user = await getCurrentUser();
                if (user?.role) setUserRole(user.role);

                setInitialRoute('Home');
            } catch (error) {
                console.warn('Auth check failed:', error);
                setInitialRoute('Login');
            } finally {
                setLoading(false);
            }
        };

        checkAuthAndRole();
    }, []);

    if (loading) return null; // ⏳ optional splash screen

    return (
        <NavigationContainer>
            <Stack.Navigator
                initialRouteName={initialRoute}
                screenOptions={screenOptions}
            >
                <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />

                {/* Conditionally render based on user role */}
                {userRole === 'admin' ? (
                    <Stack.Screen name="AdminStack" component={AdminStack} options={{ headerShown: false }} />
                ) : userRole === 'extension_officer' || userRole === 'operator' ? (
                    <Stack.Screen name="OperatorStack" component={OperatorStack} options={{ headerShown: false }} />
                ) : (
                    <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
                )}
            </Stack.Navigator>
        </NavigationContainer>
    );
};

export default AppNavigator;
