import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { checkConnectivity } from '../services/sync';

const OfflineIndicator = () => {
    const [isOnline, setIsOnline] = useState(true);

    useEffect(() => {
        const checkConnection = async () => {
            const online = await checkConnectivity();
            setIsOnline(online);
        };

        checkConnection();
        const interval = setInterval(checkConnection, 5000);

        return () => clearInterval(interval);
    }, []);

    if (isOnline) return null;

    return (
        <View style={styles.container}>
            <Text style={styles.text}>📴 Offline Mode - Data will sync when online</Text>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: '#FF9800',
        padding: 10,
        alignItems: 'center',
    },
    text: {
        color: '#fff',
        fontSize: 12,
        fontWeight: '600',
    },
});

export default OfflineIndicator;