import * as Network from 'expo-network';
import {
    getPendingFarmers,
    getLandParcels,
    getCrops,
    updateSyncStatus
} from './database';
import { syncFarmers } from './api';

// Check network connectivity
export const checkConnectivity = async () => {
    const networkState = await Network.getNetworkStateAsync();
    return networkState.isConnected && networkState.isInternetReachable;
};

// Sync pending farmers to backend
export const syncPendingFarmers = async () => {
    try {
        // Check connectivity
        const isConnected = await checkConnectivity();
        if (!isConnected) {
            throw new Error('No internet connection');
        }

        // Get all pending farmers
        const pendingFarmers = await getPendingFarmers();

        if (pendingFarmers.length === 0) {
            return {
                success: true,
                message: 'No farmers to sync',
                synced: 0
            };
        }

        // Prepare farmers data with related records
        const farmersToSync = await Promise.all(
            pendingFarmers.map(async (farmer) => {
                const landParcels = await getLandParcels(farmer.temp_id);
                const crops = await getCrops(farmer.temp_id);

                return {
                    temp_id: farmer.temp_id,
                    personal_info: {
                        first_name: farmer.first_name,
                        last_name: farmer.last_name,
                        phone_primary: farmer.phone_primary,
                        phone_alternate: farmer.phone_alternate,
                        email: farmer.email,
                        date_of_birth: farmer.date_of_birth,
                        gender: farmer.gender
                    },
                    address: {
                        province: farmer.province,
                        district: farmer.district,
                        village: farmer.village,
                        chiefdom: farmer.chiefdom,
                        gps_coordinates: {
                            latitude: farmer.latitude,
                            longitude: farmer.longitude
                        }
                    },
                    nrc_number: farmer.nrc_number,
                    land_parcels: landParcels.map(parcel => ({
                        parcel_id: parcel.parcel_id,
                        total_area: parcel.total_area,
                        ownership_type: parcel.ownership_type,
                        land_type: parcel.land_type,
                        soil_type: parcel.soil_type,
                        gps_coordinates: {
                            latitude: parcel.latitude,
                            longitude: parcel.longitude
                        }
                    })),
                    current_crops: crops.map(crop => ({
                        crop_name: crop.crop_name,
                        variety: crop.variety,
                        area_allocated: crop.area_allocated,
                        planting_date: crop.planting_date,
                        expected_harvest_date: crop.expected_harvest_date,
                        irrigation_method: crop.irrigation_method,
                        estimated_yield: crop.estimated_yield,
                        season: crop.season
                    })),
                    registration_status: 'pending_verification'
                };
            })
        );

        // Sync to backend
        const result = await syncFarmers(farmersToSync);

        // Update local database sync status
        for (const syncResult of result.results) {
            if (syncResult.status === 'created' || syncResult.status === 'updated') {
                await updateSyncStatus(
                    syncResult.temp_id,
                    'synced',
                    syncResult.farmer_id
                );
            }
        }

        return {
            success: true,
            message: `Synced ${result.successful} farmers`,
            synced: result.successful,
            failed: result.failed,
            errors: result.errors
        };

    } catch (error) {
        console.error('Sync error:', error);
        return {
            success: false,
            message: error.message || 'Sync failed',
            synced: 0
        };
    }
};

// Auto sync when connection is available
export const setupAutoSync = (interval = 300000) => { // 5 minutes
    return setInterval(async () => {
        const isConnected = await checkConnectivity();
        if (isConnected) {
            await syncPendingFarmers();
        }
    }, interval);
};


// ============================================
// File: mobile/src/utils/location.js
// ============================================
import * as Location from 'expo-location';

export const getCurrentLocation = async () => {
    try {
        // Request permission
        const { status } = await Location.requestForegroundPermissionsAsync();

        if (status !== 'granted') {
            throw new Error('Location permission denied');
        }

        // Get current position with high accuracy
        const location = await Location.getCurrentPositionAsync({
            accuracy: Location.Accuracy.High,
        });

        return {
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
            accuracy: location.coords.accuracy,
            timestamp: new Date(location.timestamp)
        };

    } catch (error) {
        console.error('Location error:', error);
        throw error;
    }
};

export const validateZambianCoordinates = (latitude, longitude) => {
    // Zambia bounds
    const minLat = -18.5;
    const maxLat = -8.0;
    const minLon = 21.5;
    const maxLon = 34.0;

    return (
        latitude >= minLat && latitude <= maxLat &&
        longitude >= minLon && longitude <= maxLon
    );
};
