import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    ActivityIndicator,
    Image,
    Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import QRCode from 'react-native-qrcode-svg';
import { getFarmerById } from '../services/database';
import * as Network from 'expo-network';
import { getFarmerFromAPI } from '../services/api';

const FarmerDetailScreen = ({ route, navigation }) => {
    const { farmerId } = route.params;
    const [farmer, setFarmer] = useState(null);
    const [loading, setLoading] = useState(true);

    // ============================================================
    // 🔹 LOAD FARMER DATA
    // ============================================================
    useEffect(() => {
        loadFarmerDetails();
    }, []);

    const loadFarmerDetails = async () => {
        setLoading(true);
        try {
            const network = await Network.getNetworkStateAsync();
            let data;

            if (network.isConnected) {
                // Online: fetch latest data from API
                data = await getFarmerFromAPI(farmerId);
            } else {
                // Offline: fetch from local SQLite
                data = await getFarmerById(farmerId);
            }

            if (!data) {
                Alert.alert('Not Found', 'Farmer details could not be loaded.');
                navigation.goBack();
                return;
            }

            setFarmer(data);
        } catch (error) {
            console.error('Error loading farmer:', error);
            Alert.alert('Error', 'Failed to load farmer details.');
        } finally {
            setLoading(false);
        }
    };

    // ============================================================
    // 🔹 RENDER FARMER DETAILS
    // ============================================================
    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#198A48" />
            </View>
        );
    }

    if (!farmer) {
        return (
            <View style={styles.centerContainer}>
                <Text style={{ color: '#999' }}>No data available</Text>
            </View>
        );
    }

    const personalInfo = farmer.personal_info || {};
    const address = farmer.address || {};

    return (
        <ScrollView style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.title}>
                    {personalInfo.first_name} {personalInfo.last_name}
                </Text>
                <Text style={styles.subtitle}>{address.village || 'Unknown Village'}</Text>
            </View>

            {/* QR Code */}
            <View style={styles.qrContainer}>
                <QRCode
                    value={farmer.farmer_id || 'N/A'}
                    size={150}
                    backgroundColor="white"
                    color="#198A48"
                />
                <Text style={styles.qrLabel}>Farmer ID: {farmer.farmer_id}</Text>
            </View>

            {/* Info Section */}
            <View style={styles.infoSection}>
                <Text style={styles.sectionTitle}>Personal Details</Text>
                <InfoRow label="Full Name" value={`${personalInfo.first_name || ''} ${personalInfo.last_name || ''}`} />
                <InfoRow label="Phone" value={personalInfo.phone_primary || 'N/A'} />
                <InfoRow label="NRC Number" value={farmer.nrc_number || 'N/A'} />
                <InfoRow label="Status" value={farmer.registration_status || 'Pending'} />
            </View>

            <View style={styles.infoSection}>
                <Text style={styles.sectionTitle}>Address</Text>
                <InfoRow label="Province" value={address.province || 'N/A'} />
                <InfoRow label="District" value={address.district || 'N/A'} />
                <InfoRow label="Village" value={address.village || 'N/A'} />
            </View>

            {/* Sync Status */}
            <View style={styles.statusContainer}>
                <Text
                    style={[
                        styles.statusBadge,
                        farmer.sync_status === 'synced' ? styles.synced : styles.pending,
                    ]}
                >
                    {farmer.sync_status === 'synced' ? '✓ Synced' : '⏳ Pending Sync'}
                </Text>
            </View>

            {/* Photo Section (Optional) */}
            {farmer.photo && (
                <View style={styles.photoSection}>
                    <Text style={styles.sectionTitle}>Farmer Photo</Text>
                    <Image
                        source={{ uri: farmer.photo }}
                        style={styles.photo}
                        resizeMode="cover"
                    />
                </View>
            )}

            {/* Back Button */}
            <TouchableOpacity
                style={styles.backButton}
                onPress={() => navigation.goBack()}
            >
                <Ionicons name="arrow-back" size={22} color="#fff" />
                <Text style={styles.backButtonText}>Back to List</Text>
            </TouchableOpacity>
        </ScrollView>
    );
};

// ============================================================
// 🔹 REUSABLE INFO ROW COMPONENT
// ============================================================
const InfoRow = ({ label, value }) => (
    <View style={styles.infoRow}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value}</Text>
    </View>
);

// ============================================================
// 🔹 STYLES
// ============================================================
const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f9fa',
        paddingHorizontal: 20,
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    header: {
        alignItems: 'center',
        marginTop: 20,
        marginBottom: 10,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#198A48',
    },
    subtitle: {
        fontSize: 16,
        color: '#7f8c8d',
    },
    qrContainer: {
        alignItems: 'center',
        marginVertical: 20,
    },
    qrLabel: {
        marginTop: 10,
        color: '#333',
        fontWeight: '600',
    },
    infoSection: {
        backgroundColor: '#fff',
        borderRadius: 10,
        padding: 15,
        marginBottom: 15,
        elevation: 2,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#198A48',
        marginBottom: 10,
    },
    infoRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 6,
    },
    infoLabel: {
        color: '#555',
        fontWeight: '600',
    },
    infoValue: {
        color: '#333',
        flexShrink: 1,
        textAlign: 'right',
    },
    statusContainer: {
        alignItems: 'center',
        marginVertical: 10,
    },
    statusBadge: {
        paddingVertical: 6,
        paddingHorizontal: 20,
        borderRadius: 20,
        fontWeight: 'bold',
        fontSize: 14,
    },
    synced: {
        backgroundColor: '#E8F5E9',
        color: '#2E7D32',
    },
    pending: {
        backgroundColor: '#FFF3E0',
        color: '#E65100',
    },
    photoSection: {
        alignItems: 'center',
        marginVertical: 20,
    },
    photo: {
        width: 180,
        height: 180,
        borderRadius: 10,
    },
    backButton: {
        backgroundColor: '#198A48',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 8,
        padding: 12,
        marginBottom: 25,
    },
    backButtonText: {
        color: '#fff',
        fontWeight: '600',
        marginLeft: 6,
    },
});

export default FarmerDetailScreen;
