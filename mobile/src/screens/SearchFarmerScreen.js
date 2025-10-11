import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ActivityIndicator,
    Alert
} from 'react-native';
import { searchFarmerByPhone } from '../services/api';

const SearchFarmerScreen = ({ navigation }) => {
    const [phone, setPhone] = useState('+260-');
    const [loading, setLoading] = useState(false);

    const handleSearch = async () => {
        if (phone.length < 10) {
            Alert.alert('Error', 'Please enter a valid phone number');
            return;
        }

        setLoading(true);
        try {
            const farmer = await searchFarmerByPhone(phone);
            navigation.navigate('FarmerDetail', { farmer });
        } catch (error) {
            Alert.alert(
                'Not Found',
                'No farmer found with this phone number'
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.searchBox}>
                <Text style={styles.label}>Search by Phone Number</Text>
                <TextInput
                    style={styles.input}
                    value={phone}
                    onChangeText={setPhone}
                    placeholder="+260-XX-XXXXXXX"
                    keyboardType="phone-pad"
                    autoFocus
                />

                <TouchableOpacity
                    style={styles.searchButton}
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

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
        padding: 20,
    },
    searchBox: {
        backgroundColor: '#fff',
        padding: 20,
        borderRadius: 10,
        elevation: 2,
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
        borderRadius: 5,
        alignItems: 'center',
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default SearchFarmerScreen;