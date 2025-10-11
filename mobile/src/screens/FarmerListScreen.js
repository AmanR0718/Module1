import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    TouchableOpacity,
    StyleSheet,
    ActivityIndicator,
    RefreshControl
} from 'react-native';
import { getAllFarmersWithStats } from '../services/database';

const FarmerListScreen = ({ navigation }) => {
    const [farmers, setFarmers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        loadFarmers();
    }, []);

    const loadFarmers = async () => {
        try {
            // For now, load from local database
            // In production, fetch from API when online
            const data = await getAllFarmersWithStats();
            setFarmers(data);
        } catch (error) {
            console.error('Error loading farmers:', error);
        } finally {
            setLoading(false);
        }
    };

    const onRefresh = async () => {
        setRefreshing(true);
        await loadFarmers();
        setRefreshing(false);
    };

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
                <Text style={[
                    styles.statusText,
                    item.sync_status === 'synced' ? styles.syncedStatus : styles.pendingStatus
                ]}>
                    {item.sync_status === 'synced' ? '✓ Synced' : '⏳ Pending'}
                </Text>
            </View>
        </TouchableOpacity>
    );

    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#198A48" />
            </View>
        );
    }

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