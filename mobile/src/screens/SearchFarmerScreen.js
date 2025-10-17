import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ActivityIndicator,
    Alert,
} from 'react-native';
import * as Network from 'expo-network';
import { searchFarmerByPhone } from '../services/api';
import { getLocalFarmers } from '../services/database';

const SearchFarmerScreen = ({ navigation }) => {
    const [phone, setPhone] = useState('+260');
    const [loading, setLoading] = useState(false);

    // ============================================================
    // 🔹 HANDLE FARMER SEARCH
    // ============================================================
    const handleSearch = async () => {
        const phonePattern = /^\+260\d{9}$/;
        if (!phonePattern.test(phone)) {
            Alert.alert('Error', 'Please enter a valid Zambian phone number (+260XXXXXXXXX)');
            return;
        }

        setLoading(true);
        try {
            const network = await Network.getNetworkStateAsync();
            let farmer = null;

            if (network.isConnected) {
                // Online — search via backend API
                farmer = await searchFarmerByPhone(phone);
            } else {
                // Offline — search locally in SQLite
                const localFarmers = await getLocalFarmers();
                farmer = localFarmers.find(f => f.phone_primary === phone);
            }

            if (farmer) {
                navigation.navigate('FarmerDetail', { farmer });
            } else {
                Alert.alert('Not Found', 'No farmer found with this phone number.');
            }
        } catch (error) {
            console.error('Search error:', error);
            Alert.alert('Error', 'Unable to search. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // ============================================================
    // 🔹 RENDER UI
    // ============================================================
    return (
        <View style={styles.container}>
            <View style={styles.searchBox}>
                <Text style={styles.label}>Search by Phone Number</Text>
                <TextInput
                    style={styles.input}
                    value={phone}
                    onChangeText={setPhone}
                    placeholder="+260XXXXXXXXX"
                    keyboardType="phone-pad"
                    autoFocus
                />

                <TouchableOpacity
                    style={[styles.searchButton, loading && { opacity: 0.7 }]}
                    onPress={handleSearch}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <Text style={styles.buttonText}>🔍 Search</Text>
                    )}
                </TouchableOpacity>
            </View>
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
        padding: 20,
        justifyContent: 'center',
    },
    searchBox: {
        backgroundColor: '#fff',
        padding: 20,
        borderRadius: 10,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
    },
    label: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        marginBottom: 10,
    },
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 5,
        padding: 15,
        fontSize: 16,
        marginBottom: 15,
    },
    searchButton: {
        backgroundColor: '#198A48',
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default SearchFarmerScreen;
