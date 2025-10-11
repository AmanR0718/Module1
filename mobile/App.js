import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import AppNavigator from './src/navigation/AppNavigator';
import { initDatabase } from './src/services/database';
import OfflineIndicator from './src/components/OfflineIndicator';
import { StyleSheet, Text, View } from 'react-native';

export default function App() {
  useEffect(() => {
    // Initialize SQLite database on app start
    initDatabase().catch(console.error);
  }, []);

  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <OfflineIndicator />
      <AppNavigator />
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});

