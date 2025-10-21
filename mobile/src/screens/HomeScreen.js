import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ScrollView,
    Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const HomeScreen = ({ navigation }) => {
    const [stats, setStats] = useState({
        totalFarmers: 0,
        recentRegistrations: 0,
        pendingSync: 0,
    });

    useEffect(() => {
        // Load dashboard stats
        loadDashboardStats();
    }, []);

    const loadDashboardStats = async () => {
        try {
            // TODO: Load actual stats from database
            setStats({
                totalFarmers: 156,
                recentRegistrations: 8,
                pendingSync: 3,
            });
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    };

    const navigateToScreen = (screenName) => {
        navigation.navigate(screenName);
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>🌾 Zambian Farmer System</Text>
                <Text style={styles.subtitle}>Dashboard Overview</Text>
            </View>

            {/* Statistics Cards */}
            <View style={styles.statsContainer}>
                <View style={styles.statCard}>
                    <Text style={styles.statNumber}>{stats.totalFarmers}</Text>
                    <Text style={styles.statLabel}>Total Farmers</Text>
                </View>
                <View style={styles.statCard}>
                    <Text style={styles.statNumber}>{stats.recentRegistrations}</Text>
                    <Text style={styles.statLabel}>Recent</Text>
                </View>
                <View style={styles.statCard}>
                    <Text style={styles.statNumber}>{stats.pendingSync}</Text>
                    <Text style={styles.statLabel}>Pending Sync</Text>
                </View>
            </View>

            {/* Action Buttons */}
            <View style={styles.actionsContainer}>
                <TouchableOpacity 
                    style={[styles.actionButton, styles.primaryButton]}
                    onPress={() => navigateToScreen('FarmerRegistrationScreen')}
                >
                    <Ionicons name="person-add" size={24} color="#fff" />
                    <Text style={styles.primaryButtonText}>Register New Farmer</Text>
                </TouchableOpacity>

                <View style={styles.secondaryButtonsRow}>
                    <TouchableOpacity 
                        style={[styles.actionButton, styles.secondaryButton]}
                        onPress={() => navigateToScreen('FarmerListScreen')}
                    >
                        <Ionicons name="list" size={20} color="#198A48" />
                        <Text style={styles.secondaryButtonText}>View Farmers</Text>
                    </TouchableOpacity>

                    <TouchableOpacity 
                        style={[styles.actionButton, styles.secondaryButton]}
                        onPress={() => navigateToScreen('SearchFarmerScreen')}
                    >
                        <Ionicons name="search" size={20} color="#198A48" />
                        <Text style={styles.secondaryButtonText}>Search</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f9fa',
    },
    header: {
        padding: 20,
        paddingTop: 40,
        alignItems: 'center',
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#2c3e50',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: '#7f8c8d',
        marginBottom: 20,
    },
    statsContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        paddingHorizontal: 20,
        marginBottom: 30,
    },
    statCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 15,
        alignItems: 'center',
        minWidth: 80,
        elevation: 2,
        boxShadow: '0px 2px 3.84px rgba(0, 0, 0, 0.25)',

    },
    statNumber: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#198A48',
    },
    statLabel: {
        fontSize: 12,
        color: '#7f8c8d',
        textAlign: 'center',
    },
    actionsContainer: {
        paddingHorizontal: 20,
    },
    actionButton: {
        borderRadius: 12,
        padding: 15,
        marginBottom: 15,
        alignItems: 'center',
        elevation: 2,
        boxShadow: '0px 2px 3.84px rgba(0, 0, 0, 0.25)',
        flexDirection: 'row',
        justifyContent: 'center',
    },
    primaryButton: {
        backgroundColor: '#198A48',
        flexDirection: 'row',
    },
    primaryButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
        marginLeft: 8,
    },
    secondaryButtonsRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    secondaryButton: {
        backgroundColor: '#fff',
        borderWidth: 1,
        borderColor: '#198A48',
        flex: 0.48,
        flexDirection: 'row',
    },
    secondaryButtonText: {
        color: '#198A48',
        fontSize: 14,
        fontWeight: '600',
        marginLeft: 8,
    },
});

export default HomeScreen;
