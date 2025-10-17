// ============================================
// File: mobile/src/services/sync.js
// Offline Farmer Sync Logic
// ============================================

import * as Network from "expo-network";
import {
    getPendingFarmers,
    getLandParcels,
    getCrops,
    updateSyncStatus,
} from "./database";
import { syncFarmers } from "./api";

let isSyncing = false; // Prevents parallel syncs

/**
 * ✅ Check if device has active internet connection
 */
export const checkConnectivity = async () => {
    try {
        const state = await Network.getNetworkStateAsync();
        return state.isConnected && state.isInternetReachable;
    } catch (error) {
        console.warn("⚠️ Network check failed:", error);
        return false;
    }
};

/**
 * 🔁 Sync all pending farmers from local SQLite to backend
 */
export const syncPendingFarmers = async () => {
    if (isSyncing) {
        console.log("⏳ Sync already in progress, skipping...");
        return;
    }

    isSyncing = true;
    console.log("🌍 Checking for pending farmers to sync...");

    try {
        const isConnected = await checkConnectivity();
        if (!isConnected) {
            throw new Error("No internet connection");
        }

        const pendingFarmers = await getPendingFarmers();
        if (pendingFarmers.length === 0) {
            console.log("✅ No pending farmers to sync.");
            return { success: true, synced: 0 };
        }

        console.log(`📦 Found ${pendingFarmers.length} unsynced farmers.`);

        // Prepare each farmer with related records
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
                        gender: farmer.gender,
                    },
                    address: {
                        province: farmer.province,
                        district: farmer.district,
                        village: farmer.village,
                        chiefdom: farmer.chiefdom,
                        gps_coordinates: {
                            latitude: farmer.latitude,
                            longitude: farmer.longitude,
                        },
                    },
                    nrc_number: farmer.nrc_number,
                    land_parcels: landParcels.map((p) => ({
                        parcel_id: p.parcel_id,
                        total_area: p.total_area,
                        ownership_type: p.ownership_type,
                        land_type: p.land_type,
                        soil_type: p.soil_type,
                        gps_coordinates: { latitude: p.latitude, longitude: p.longitude },
                    })),
                    current_crops: crops.map((c) => ({
                        crop_name: c.crop_name,
                        variety: c.variety,
                        area_allocated: c.area_allocated,
                        planting_date: c.planting_date,
                        expected_harvest_date: c.expected_harvest_date,
                        irrigation_method: c.irrigation_method,
                        estimated_yield: c.estimated_yield,
                        season: c.season,
                    })),
                    registration_status: "pending_verification",
                };
            })
        );

        // Send to backend
        const result = await syncFarmers(farmersToSync);
        console.log(`✅ Sync complete: ${result.successful} successful, ${result.failed} failed.`);

        // Update local DB
        for (const syncResult of result.results || []) {
            if (["created", "updated"].includes(syncResult.status)) {
                await updateSyncStatus(syncResult.temp_id, "synced", syncResult.farmer_id);
                console.log(`🟢 Farmer ${syncResult.farmer_id} marked as synced.`);
            }
        }

        return {
            success: true,
            synced: result.successful,
            failed: result.failed,
            errors: result.errors,
        };
    } catch (error) {
        console.error("❌ Sync error:", error.message);
        return { success: false, message: error.message, synced: 0 };
    } finally {
        isSyncing = false;
    }
};

/**
 * 🔄 Auto Sync (every X minutes)
 */
export const setupAutoSync = (interval = 300000) => {
    console.log(`🕒 Auto sync set for every ${interval / 1000 / 60} minutes.`);
    return setInterval(async () => {
        const isConnected = await checkConnectivity();
        if (isConnected) await syncPendingFarmers();
    }, interval);
};
