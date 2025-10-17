import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import * as Network from 'expo-network';
import { registerFarmer } from '../services/api';
import { saveFarmerOffline } from '../services/database';

const FarmerRegistrationScreen = ({ navigation }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    phone: '',
    nrcNumber: '',
    province: '',
    district: '',
    village: '',
  });
  const [loading, setLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const validateForm = () => {
    const { firstName, lastName, phone, nrcNumber, province, district, village } = formData;
    if (!firstName || !lastName || !phone || !nrcNumber || !province || !district || !village) {
      Alert.alert('Error', 'Please fill in all fields.');
      return false;
    }

    const phonePattern = /^\+260\d{9}$/;
    const nrcPattern = /^\d{6}\/\d{2}\/\d{1}$/;

    if (!phonePattern.test(phone)) {
      Alert.alert('Error', 'Phone number must be in format +260XXXXXXXXX');
      return false;
    }
    if (!nrcPattern.test(nrcNumber)) {
      Alert.alert('Error', 'NRC number must follow format 123456/12/1');
      return false;
    }

    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      const network = await Network.getNetworkStateAsync();

      if (network.isConnected) {
        // Online: Register via API
        const response = await registerFarmer(formData);
        Alert.alert('✅ Success', 'Farmer registered successfully!');
        console.log('Registered Farmer:', response);
      } else {
        // Offline: Save locally
        await saveFarmerOffline({
          farmer_id: `OFF-${Date.now()}`,
          personal_info: {
            first_name: formData.firstName,
            last_name: formData.lastName,
            phone_primary: formData.phone,
          },
          address: {
            province: formData.province,
            district: formData.district,
            village: formData.village,
          },
          nrc_number: formData.nrcNumber,
        });
        Alert.alert('📦 Offline', 'Farmer saved locally. Will sync later.');
      }

      navigation.navigate('FarmerList');
    } catch (error) {
      console.error('Registration error:', error);
      Alert.alert('Error', 'Failed to register farmer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.form}>
        <Text style={styles.title}>🌾 Register New Farmer</Text>

        <TextInput
          style={styles.input}
          placeholder="First Name"
          value={formData.firstName}
          onChangeText={(value) => handleInputChange('firstName', value)}
        />

        <TextInput
          style={styles.input}
          placeholder="Last Name"
          value={formData.lastName}
          onChangeText={(value) => handleInputChange('lastName', value)}
        />

        <TextInput
          style={styles.input}
          placeholder="Phone Number (+260...)"
          value={formData.phone}
          onChangeText={(value) => handleInputChange('phone', value)}
          keyboardType="phone-pad"
        />

        <TextInput
          style={styles.input}
          placeholder="NRC Number (123456/12/1)"
          value={formData.nrcNumber}
          onChangeText={(value) => handleInputChange('nrcNumber', value)}
        />

        <TextInput
          style={styles.input}
          placeholder="Province"
          value={formData.province}
          onChangeText={(value) => handleInputChange('province', value)}
        />

        <TextInput
          style={styles.input}
          placeholder="District"
          value={formData.district}
          onChangeText={(value) => handleInputChange('district', value)}
        />

        <TextInput
          style={styles.input}
          placeholder="Village"
          value={formData.village}
          onChangeText={(value) => handleInputChange('village', value)}
        />

        <TouchableOpacity
          style={[styles.submitButton, loading && { opacity: 0.7 }]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitButtonText}>📝 Register Farmer</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity style={styles.cancelButton} onPress={() => navigation.goBack()}>
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  form: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#2c3e50',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    marginBottom: 16,
    backgroundColor: '#fff',
    fontSize: 16,
  },
  submitButton: {
    backgroundColor: '#198A48',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 16,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  cancelButton: {
    padding: 15,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#7f8c8d',
    fontSize: 16,
  },
});

export default FarmerRegistrationScreen;
