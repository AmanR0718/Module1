import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    TouchableOpacity,
    StyleSheet,
    ActivityIndicator,
    RefreshControl,
    Alert,
} from 'react-native';
import * as Network from 'expo-network';
import { getAllFarmersWithStats, saveFarmerOffline } from '../services/database';
import { getAllFarmersFromAPI } from '../services/api';

const FarmerListScreen = ({ navigation }) => {
    const [farmers, setFarmers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        loadFarmers();
    }, []);

    // ============================================================
    // 🔹 LOAD FARMERS (online preferred, offline fallback)
    // ============================================================
    const loadFarmers = async () => {
        setLoading(true);
        try {
            const network = await Network.getNetworkStateAsync();
            let data = [];

            if (network.isConnected) {
                // 🌐 Fetch from API
                const apiFarmers = await getAllFarmersFromAPI();

                // Cache to local DB for offline use
                for (const farmer of apiFarmers) {
                    await saveFarmerOffline({
                        farmer_id: farmer.farmer_id,
                        first_name: farmer.personal_info?.first_name || '',
                        last_name: farmer.personal_info?.last_name || '',
                        phone_primary: farmer.personal_info?.phone_primary || '',
                        province: farmer.address?.province || '',
                        district: farmer.address?.district || '',
                        sync_status: 'synced',
                    });
                }

                data = apiFarmers.map((f) => ({
                    id: f._id || f.farmer_id,
                    first_name: f.personal_info?.first_name,
                    last_name: f.personal_info?.last_name,
                    phone_primary: f.personal_info?.phone_primary,
                    province: f.address?.province,
                    district: f.address?.district,
                    sync_status: 'synced',
                }));
            } else {
                // 📦 Offline: Load from SQLite
                data = await getAllFarmersWithStats();
            }

            setFarmers(data);
        } catch (error) {
            console.error('Error loading farmers:', error);
            Alert.alert('Error', 'Failed to load farmers.');
        } finally {
            setLoading(false);
        }
    };

    // ============================================================
    // 🔹 REFRESH HANDLER
    // ============================================================
    const onRefresh = async () => {
        setRefreshing(true);
        await loadFarmers();
        setRefreshing(false);
    };

    // ============================================================
    // 🔹 RENDER SINGLE FARMER CARD
    // ============================================================
    const renderFarmerItem = ({ item }) => (
        <TouchableOpacity
            style={styles.farmerCard}
            onPress={() => navigation.navigate('FarmerDetail', { farmerId: item.farmer_id })}
        >
            <View style={styles.farmerInfo}>
                <Text style={styles.farmerName}>
                    {item.first_name} {item.last_name}
                </Text>
                <Text style={styles.farmerDetails}>
                    {item.district}, {item.province}
                </Text>
                <Text style={styles.farmerPhone}>{item.phone_primary}</Text>
            </View>

            <View style={styles.statusBadge}>
                <Text
                    style={[
                        styles.statusText,
                        item.sync_status === 'synced' ? styles.syncedStatus : styles.pendingStatus,
                    ]}
                >
                    {item.sync_status === 'synced' ? '✓ Synced' : '⏳ Pending'}
                </Text>
            </View>
        </TouchableOpacity>
    );

    // ============================================================
    // 🔹 LOADING VIEW
    // ============================================================
    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#198A48" />
            </View>
        );
    }

    // ============================================================
    // 🔹 MAIN RENDER
    // ============================================================
    return (
        <View style={styles.container}>
            <FlatList
                data={farmers}
                renderItem={renderFarmerItem}
                keyExtractor={(item) => item.id?.toString()}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
                ListEmptyComponent={
                    <View style={styles.emptyContainer}>
                        <Text style={styles.emptyText}>No farmers registered yet</Text>
                    </View>
                }
            />
        </View>
    );
};

// ============================================================
// 🔹 STYLES
// ============================================================
const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    farmerCard: {
        backgroundColor: '#fff',
        padding: 15,
        marginHorizontal: 15,
        marginVertical: 8,
        borderRadius: 10,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    farmerInfo: {
        flex: 1,
    },
    farmerName: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
    },
    farmerDetails: {
        fontSize: 14,
        color: '#666',
        marginTop: 4,
    },
    farmerPhone: {
        fontSize: 12,
        color: '#999',
        marginTop: 2,
    },
    statusBadge: {
        paddingHorizontal: 10,
        paddingVertical: 5,
        borderRadius: 12,
    },
    statusText: {
        fontSize: 12,
        fontWeight: '600',
    },
    syncedStatus: {
        color: '#4CAF50',
    },
    pendingStatus: {
        color: '#FF9800',
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingTop: 100,
    },
    emptyText: {
        fontSize: 16,
        color: '#999',
    },
});

export default FarmerListScreen;
