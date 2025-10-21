import { shadowStyle } from '../styles/shadow';
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TouchableOpacity,
    StyleSheet,
    ScrollView,
    Alert,
    RefreshControl
} from 'react-native';
import { getAllFarmersWithStats } from '../services/database';
import { checkConnectivity, syncPendingFarmers } from '../services/sync';
import { logout } from '../services/api';

const HomeScreen = ({ navigation }) => {
    const [stats, setStats] = useState({ total: 0, pending: 0, synced: 0 });
    const [isOnline, setIsOnline] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [syncing, setSyncing] = useState(false);

    useEffect(() => {
        loadStats();
        checkConnection();
        const interval = setInterval(checkConnection, 10000); // Check every 10s
        return () => clearInterval(interval);
    }, []);

    const loadStats = async () => {
        try {
            const data = await getAllFarmersWithStats();
            setStats(data);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    };

    const checkConnection = async () => {
        const connected = await checkConnectivity();
        setIsOnline(connected);
    };

    const handleSync = async () => {
        if (!isOnline) {
            Alert.alert('No Connection', 'Please connect to internet to sync');
            return;
        }

        if (stats.pending === 0) {
            Alert.alert('Nothing to Sync', 'All farmers are already synced');
            return;
        }

        setSyncing(true);
        try {
            const result = await syncPendingFarmers();

            if (result.success) {
                Alert.alert('Success', result.message);
                await loadStats();
            } else {
                Alert.alert('Sync Failed', result.message);
            }
        } catch (error) {
            Alert.alert('Error', error.message);
        } finally {
            setSyncing(false);
        }
    };

    const handleLogout = async () => {
        Alert.alert(
            'Logout',
            'Are you sure you want to logout?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Logout',
                    style: 'destructive',
                    onPress: async () => {
                        await logout();
                        navigation.replace('Login');
                    }
                }
            ]
        );
    };

    const onRefresh = async () => {
        setRefreshing(true);
        await loadStats();
        await checkConnection();
        setRefreshing(false);
    };

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
        >
            <View style={styles.header}>
                <Text style={styles.headerTitle}>Dashboard</Text>
                <View style={[styles.badge, isOnline ? styles.onlineBadge : styles.offlineBadge]}>
                    <Text style={styles.badgeText}>{isOnline ? 'Online' : 'Offline'}</Text>
                </View>
            </View>

            {/* Statistics Cards */}
            <View style={styles.statsContainer}>
                <View style={styles.statCard}>
                    <Text style={styles.statNumber}>{stats.total}</Text>
                    <Text style={styles.statLabel}>Total Farmers</Text>
                </View>

                <View style={[styles.statCard, styles.pendingCard]}>
                    <Text style={styles.statNumber}>{stats.pending}</Text>
                    <Text style={styles.statLabel}>Pending Sync</Text>
                </View>

                <View style={[styles.statCard, styles.syncedCard]}>
                    <Text style={styles.statNumber}>{stats.synced}</Text>
                    <Text style={styles.statLabel}>Synced</Text>
                </View>
            </View>

            {/* Action Buttons */}
            <View style={styles.actionsContainer}>
                <TouchableOpacity
                    style={styles.actionButton}
                    onPress={() => navigation.navigate('FarmerRegistration')}
                >
                    <Text style={styles.actionIcon}>➕</Text>
                    <Text style={styles.actionText}>New Registration</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.actionButton, styles.syncButton]}
                    onPress={handleSync}
                    disabled={syncing || !isOnline}
                >
                    <Text style={styles.actionIcon}>🔄</Text>
                    <Text style={styles.actionText}>
                        {syncing ? 'Syncing...' : 'Sync Data'}
                    </Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.actionButton}
                    onPress={() => navigation.navigate('FarmerList')}
                >
                    <Text style={styles.actionIcon}>📋</Text>
                    <Text style={styles.actionText}>View Farmers</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.actionButton}
                    onPress={() => navigation.navigate('SearchFarmer')}
                >
                    <Text style={styles.actionIcon}>🔍</Text>
                    <Text style={styles.actionText}>Search Farmer</Text>
                </TouchableOpacity>
            </View>

            {/* Logout Button */}
            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
                <Text style={styles.logoutText}>Logout</Text>
            </TouchableOpacity>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: '#198A48',
        padding:
  ...shadowStyle, 20,
        paddingTop: 50,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    headerTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#fff',
    },
    badge: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 12,
    },
    onlineBadge: {
        backgroundColor: '#4CAF50',
    },
    offlineBadge: {
        backgroundColor: '#FF5252',
    },
    badgeText: {
        color: '#fff',
        fontSize: 12,
        fontWeight: 'bold',
    },
    statsContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        padding: 15,
        gap: 10,
    },
    statCard: {
        flex: 1,
        backgroundColor: '#fff',
        padding: 15,
        borderRadius: 10,
        alignItems: 'center',
        elevation: 2,
    },
    pendingCard: {
        backgroundColor: '#FFF3E0',
    },
    syncedCard: {
        backgroundColor: '#E8F5E9',
    },
    statNumber: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#333',
    },
    statLabel: {
        fontSize: 12,
        color: '#666',
        marginTop: 5,
    },
    actionsContainer: {
        padding: 15,
        gap: 10,
    },
    actionButton: {
        backgroundColor: '#fff',
        flexDirection: 'row',
        alignItems: 'center',
        padding: 20,
        borderRadius: 10,
        elevation: 2,
    },
    syncButton: {
        backgroundColor: '#E3F2FD',
    },
    actionIcon: {
        fontSize: 24,
        marginRight: 15,
    },
    actionText: {
        fontSize: 16,
        color: '#333',
        fontWeight: '500',
    },
    logoutButton: {
        margin: 15,
        padding: 15,
        backgroundColor: '#FF5252',
        borderRadius: 10,
        alignItems: 'center',
    },
    logoutText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default HomeScreen;


// ============================================
// File: mobile/src/screens/FarmerRegistrationScreen.js
// ============================================
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    ScrollView,
    StyleSheet,
    Alert,
    ActivityIndicator,
    Platform
} from 'react-native';
import { Formik } from 'formik';
import { personalInfoSchema } from '../utils/validation';
import { insertFarmer, insertLandParcel, insertCrop } from '../services/database';
import { getCurrentLocation } from '../utils/location';
import { getProvinces, getDistricts } from '../services/api';
import RNPickerSelect from 'react-native-picker-select';

const FarmerRegistrationScreen = ({ navigation }) => {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [location, setLocation] = useState(null);
    const [provinces, setProvinces] = useState([]);
    const [districts, setDistricts] = useState([]);
    const [tempId, setTempId] = useState('');

    useEffect(() => {
        loadProvinces();
        captureLocation();
    }, []);

    const loadProvinces = async () => {
        try {
            const data = await getProvinces();
            setProvinces(data.map(p => ({ label: p, value: p })));
        } catch (error) {
            console.error('Error loading provinces:', error);
        }
    };

    const loadDistricts = async (province) => {
        try {
            const data = await getDistricts(province);
            setDistricts(data.map(d => ({ label: d, value: d })));
        } catch (error) {
            console.error('Error loading districts:', error);
        }
    };

    const captureLocation = async () => {
        try {
            const loc = await getCurrentLocation();
            setLocation(loc);
        } catch (error) {
            Alert.alert('Location Error', 'Failed to get GPS location');
        }
    };

    const handlePersonalInfoSubmit = async (values) => {
        setLoading(true);
        try {
            // Generate temporary ID
            const tempFarmerId = `TEMP_${Date.now()}`;
            setTempId(tempFarmerId);

            // Save to local database
            await insertFarmer({
                temp_id: tempFarmerId,
                ...values,
                latitude: location?.latitude,
                longitude: location?.longitude,
            });

            setStep(2);
        } catch (error) {
            Alert.alert('Error', error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleLandDetailsSubmit = async (values) => {
        setLoading(true);
        try {
            await insertLandParcel(tempId, {
                parcel_id: `PARCEL_${Date.now()}`,
                ...values,
                latitude: location?.latitude,
                longitude: location?.longitude,
            });
            setStep(3);
        } catch (error) {
            Alert.alert('Error', error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleCropDetailsSubmit = async (values) => {
        setLoading(true);
        try {
            await insertCrop(tempId, values);

            Alert.alert(
                'Success',
                'Farmer registered successfully!',
                [
                    {
                        text: 'OK',
                        onPress: () => navigation.navigate('Home')
                    }
                ]
            );
        } catch (error) {
            Alert.alert('Error', error.message);
        } finally {
            setLoading(false);
        }
    };

    // Step 1: Personal Information
    const renderPersonalInfoForm = () => (
        <Formik
            initialValues={{
                first_name: '',
                last_name: '',
                phone_primary: '+260-',
                phone_alternate: '',
                email: '',
                date_of_birth: '',
                gender: '',
                nrc_number: '',
                province: '',
                district: '',
                village: '',
                chiefdom: '',
            }}
            validationSchema={personalInfoSchema}
            onSubmit={handlePersonalInfoSubmit}
        >
            {({ handleChange, handleSubmit, values, errors, touched, setFieldValue }) => (
                <View>
                    <Text style={styles.label}>First Name *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.first_name}
                        onChangeText={handleChange('first_name')}
                        placeholder="Enter first name"
                    />
                    {touched.first_name && errors.first_name && (
                        <Text style={styles.errorText}>{errors.first_name}</Text>
                    )}

                    <Text style={styles.label}>Last Name *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.last_name}
                        onChangeText={handleChange('last_name')}
                        placeholder="Enter last name"
                    />
                    {touched.last_name && errors.last_name && (
                        <Text style={styles.errorText}>{errors.last_name}</Text>
                    )}

                    <Text style={styles.label}>Primary Phone *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.phone_primary}
                        onChangeText={handleChange('phone_primary')}
                        placeholder="+260-XX-XXXXXXX"
                        keyboardType="phone-pad"
                    />
                    {touched.phone_primary && errors.phone_primary && (
                        <Text style={styles.errorText}>{errors.phone_primary}</Text>
                    )}

                    <Text style={styles.label}>NRC Number *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.nrc_number}
                        onChangeText={handleChange('nrc_number')}
                        placeholder="XXXXXX/XX/X"
                    />
                    {touched.nrc_number && errors.nrc_number && (
                        <Text style={styles.errorText}>{errors.nrc_number}</Text>
                    )}

                    <Text style={styles.label}>Date of Birth *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.date_of_birth}
                        onChangeText={handleChange('date_of_birth')}
                        placeholder="YYYY-MM-DD"
                    />
                    {touched.date_of_birth && errors.date_of_birth && (
                        <Text style={styles.errorText}>{errors.date_of_birth}</Text>
                    )}

                    <Text style={styles.label}>Gender *</Text>
                    <RNPickerSelect
                        style={pickerSelectStyles}
                        value={values.gender}
                        onValueChange={(value) => setFieldValue('gender', value)}
                        items={[
                            { label: 'Male', value: 'male' },
                            { label: 'Female', value: 'female' },
                            { label: 'Other', value: 'other' },
                        ]}
                        placeholder={{ label: 'Select gender...', value: null }}
                    />

                    <Text style={styles.label}>Province *</Text>
                    <RNPickerSelect
                        style={pickerSelectStyles}
                        value={values.province}
                        onValueChange={(value) => {
                            setFieldValue('province', value);
                            loadDistricts(value);
                        }}
                        items={provinces}
                        placeholder={{ label: 'Select province...', value: null }}
                    />

                    <Text style={styles.label}>District *</Text>
                    <RNPickerSelect
                        style={pickerSelectStyles}
                        value={values.district}
                        onValueChange={(value) => setFieldValue('district', value)}
                        items={districts}
                        placeholder={{ label: 'Select district...', value: null }}
                    />

                    <Text style={styles.label}>Village *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.village}
                        onChangeText={handleChange('village')}
                        placeholder="Enter village name"
                    />

                    {location && (
                        <View style={styles.locationCard}>
                            <Text style={styles.locationText}>📍 GPS Location Captured</Text>
                            <Text style={styles.locationCoords}>
                                Lat: {location.latitude.toFixed(6)}, Lon: {location.longitude.toFixed(6)}
                            </Text>
                        </View>
                    )}

                    <TouchableOpacity
                        style={styles.submitButton}
                        onPress={handleSubmit}
                        disabled={loading}
                    >
                        {loading ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <Text style={styles.submitButtonText}>Next: Land Details</Text>
                        )}
                    </TouchableOpacity>
                </View>
            )}
        </Formik>
    );

    // Step 2: Land Details
    const renderLandDetailsForm = () => (
        <Formik
            initialValues={{
                total_area: '',
                ownership_type: '',
                land_type: '',
                soil_type: '',
            }}
            onSubmit={handleLandDetailsSubmit}
        >
            {({ handleChange, handleSubmit, values, setFieldValue }) => (
                <View>
                    <Text style={styles.label}>Total Area (Hectares) *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.total_area}
                        onChangeText={handleChange('total_area')}
                        placeholder="e.g., 2.5"
                        keyboardType="decimal-pad"
                    />

                    <Text style={styles.label}>Ownership Type *</Text>
                    <RNPickerSelect
                        style={pickerSelectStyles}
                        value={values.ownership_type}
                        onValueChange={(value) => setFieldValue('ownership_type', value)}
                        items={[
                            { label: 'Owned', value: 'owned' },
                            { label: 'Leased', value: 'leased' },
                            { label: 'Shared', value: 'shared' },
                        ]}
                        placeholder={{ label: 'Select ownership type...', value: null }}
                    />

                    <Text style={styles.label}>Land Type *</Text>
                    <RNPickerSelect
                        style={pickerSelectStyles}
                        value={values.land_type}
                        onValueChange={(value) => setFieldValue('land_type', value)}
                        items={[
                            { label: 'Irrigated', value: 'irrigated' },
                            { label: 'Non-Irrigated', value: 'non_irrigated' },
                        ]}
                        placeholder={{ label: 'Select land type...', value: null }}
                    />

                    <Text style={styles.label}>Soil Type</Text>
                    <TextInput
                        style={styles.input}
                        value={values.soil_type}
                        onChangeText={handleChange('soil_type')}
                        placeholder="e.g., Clay Loam"
                    />

                    <View style={styles.buttonRow}>
                        <TouchableOpacity
                            style={[styles.button, styles.backButton]}
                            onPress={() => setStep(1)}
                        >
                            <Text style={styles.buttonText}>Back</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={[styles.button, styles.submitButton]}
                            onPress={handleSubmit}
                            disabled={loading}
                        >
                            {loading ? (
                                <ActivityIndicator color="#fff" />
                            ) : (
                                <Text style={styles.submitButtonText}>Next: Crop Details</Text>
                            )}
                        </TouchableOpacity>
                    </View>
                </View>
            )}
        </Formik>
    );

    // Step 3: Crop Details
    const renderCropDetailsForm = () => (
        <Formik
            initialValues={{
                crop_name: '',
                variety: '',
                area_allocated: '',
                planting_date: '',
                expected_harvest_date: '',
                irrigation_method: '',
                estimated_yield: '',
                season: '2024/2025',
            }}
            onSubmit={handleCropDetailsSubmit}
        >
            {({ handleChange, handleSubmit, values, setFieldValue }) => (
                <View>
                    <Text style={styles.label}>Crop Name *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.crop_name}
                        onChangeText={handleChange('crop_name')}
                        placeholder="e.g., Maize"
                    />

                    <Text style={styles.label}>Variety</Text>
                    <TextInput
                        style={styles.input}
                        value={values.variety}
                        onChangeText={handleChange('variety')}
                        placeholder="e.g., Hybrid"
                    />

                    <Text style={styles.label}>Area Allocated (Hectares) *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.area_allocated}
                        onChangeText={handleChange('area_allocated')}
                        placeholder="e.g., 1.5"
                        keyboardType="decimal-pad"
                    />

                    <Text style={styles.label}>Planting Date</Text>
                    <TextInput
                        style={styles.input}
                        value={values.planting_date}
                        onChangeText={handleChange('planting_date')}
                        placeholder="YYYY-MM-DD"
                    />

                    <Text style={styles.label}>Expected Harvest Date</Text>
                    <TextInput
                        style={styles.input}
                        value={values.expected_harvest_date}
                        onChangeText={handleChange('expected_harvest_date')}
                        placeholder="YYYY-MM-DD"
                    />

                    <Text style={styles.label}>Irrigation Method</Text>
                    <RNPickerSelect
                        style={pickerSelectStyles}
                        value={values.irrigation_method}
                        onValueChange={(value) => setFieldValue('irrigation_method', value)}
                        items={[
                            { label: 'Drip', value: 'drip' },
                            { label: 'Sprinkler', value: 'sprinkler' },
                            { label: 'Flood', value: 'flood' },
                            { label: 'Rain-fed', value: 'rainfed' },
                        ]}
                        placeholder={{ label: 'Select method...', value: null }}
                    />

                    <Text style={styles.label}>Estimated Yield (Tons)</Text>
                    <TextInput
                        style={styles.input}
                        value={values.estimated_yield}
                        onChangeText={handleChange('estimated_yield')}
                        placeholder="e.g., 6.0"
                        keyboardType="decimal-pad"
                    />

                    <Text style={styles.label}>Season *</Text>
                    <TextInput
                        style={styles.input}
                        value={values.season}
                        onChangeText={handleChange('season')}
                        placeholder="2024/2025"
                    />

                    <View style={styles.buttonRow}>
                        <TouchableOpacity
                            style={[styles.button, styles.backButton]}
                            onPress={() => setStep(2)}
                        >
                            <Text style={styles.buttonText}>Back</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={[styles.button, styles.submitButton]}
                            onPress={handleSubmit}
                            disabled={loading}
                        >
                            {loading ? (
                                <ActivityIndicator color="#fff" />
                            ) : (
                                <Text style={styles.submitButtonText}>Complete Registration</Text>
                            )}
                        </TouchableOpacity>
                    </View>
                </View>
            )}
        </Formik>
    );

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>New Farmer Registration</Text>
                <Text style={styles.stepIndicator}>Step {step} of 3</Text>
            </View>

            <View style={styles.progressBar}>
                <View style={[styles.progressFill, { width: `${(step / 3) * 100}%` }]} />
            </View>

            <View style={styles.formContainer}>
                {step === 1 && renderPersonalInfoForm()}
                {step === 2 && renderLandDetailsForm()}
                {step === 3 && renderCropDetailsForm()}
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: '#198A48',
        padding: 20,
        paddingTop: 50,
    },
    headerTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#fff',
    },
    stepIndicator: {
        fontSize: 14,
        color: '#fff',
        marginTop: 5,
    },
    progressBar: {
        height: 4,
        backgroundColor: '#e0e0e0',
    },
    progressFill: {
        height: '100%',
        backgroundColor: '#4CAF50',
    },
    formContainer: {
        padding: 20,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: '#333',
        marginTop: 15,
        marginBottom: 5,
    },
    input: {
        backgroundColor: '#fff',
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 5,
        padding: 12,
        fontSize: 16,
    },
    errorText: {
        color: '#FF5252',
        fontSize: 12,
        marginTop: 5,
    },
    locationCard: {
        backgroundColor: '#E8F5E9',
        padding: 15,
        borderRadius: 5,
        marginTop: 15,
    },
    locationText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#2E7D32',
    },
    locationCoords: {
        fontSize: 12,
        color: '#388E3C',
        marginTop: 5,
    },
    buttonRow: {
        flexDirection: 'row',
        gap: 10,
        marginTop: 20,
    },
    button: {
        flex: 1,
        padding: 15,
        borderRadius: 5,
        alignItems: 'center',
    },
    backButton: {
        backgroundColor: '#757575',
    },
    submitButton: {
        backgroundColor: '#198A48',
        marginTop: 20,
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    submitButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});

const pickerSelectStyles = StyleSheet.create({
    inputIOS: {
        backgroundColor: '#fff',
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 5,
        padding: 12,
        fontSize: 16,
        color: '#333',
    },
    inputAndroid: {
        backgroundColor: '#fff',
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 5,
        padding: 12,
        fontSize: 16,
        color: '#333',
    },
});

export default FarmerRegistrationScreen;