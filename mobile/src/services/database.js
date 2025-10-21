// ============================================
// File: mobile/src/services/database.js
// Local SQLite database for offline farmers
// ============================================

import { Platform } from "react-native";

let db = null;

// 🧩 Fallback mock DB for web
const createMockDB = () => ({
  transaction: (cb) =>
    cb({
      executeSql: (query, params = [], success, error) => {
        console.log("⚠️ [MOCK DB] Query ignored (web mode):", query, params);
        success?.(null, { rows: { _array: [] } });
      },
    }),
});

// ✅ Initialize DB safely
export const initDatabase = () => {
  return new Promise((resolve, reject) => {
    if (Platform.OS === "web") {
      console.warn("⚠️ SQLite not supported on web — using mock DB.");
      db = createMockDB();
      return resolve(true);
    }

    try {
      const SQLite = require("expo-sqlite");
      db = SQLite.openDatabase("zambian_farmers.db");
    } catch (err) {
      console.error("❌ Failed to load expo-sqlite:", err);
      db = createMockDB();
      return resolve(false);
    }

    db.transaction(
      (tx) => {
        // Farmers
        tx.executeSql(
          `CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp_id TEXT UNIQUE,
            farmer_id TEXT,
            nrc_number TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone_primary TEXT NOT NULL,
            phone_alternate TEXT,
            email TEXT,
            date_of_birth TEXT,
            gender TEXT,
            province TEXT,
            district TEXT,
            village TEXT,
            chiefdom TEXT,
            latitude REAL,
            longitude REAL,
            sync_status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
          );`
        );

        // Land Parcels
        tx.executeSql(
          `CREATE TABLE IF NOT EXISTS land_parcels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp_farmer_id TEXT,
            parcel_id TEXT,
            total_area REAL,
            ownership_type TEXT,
            land_type TEXT,
            soil_type TEXT,
            latitude REAL,
            longitude REAL,
            FOREIGN KEY (temp_farmer_id) REFERENCES farmers (temp_id)
          );`
        );

        // Crops
        tx.executeSql(
          `CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp_farmer_id TEXT,
            crop_name TEXT,
            variety TEXT,
            area_allocated REAL,
            planting_date TEXT,
            expected_harvest_date TEXT,
            irrigation_method TEXT,
            estimated_yield REAL,
            season TEXT,
            FOREIGN KEY (temp_farmer_id) REFERENCES farmers (temp_id)
          );`
        );

        // Documents
        tx.executeSql(
          `CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp_farmer_id TEXT,
            doc_type TEXT,
            doc_number TEXT,
            file_path TEXT,
            FOREIGN KEY (temp_farmer_id) REFERENCES farmers (temp_id)
          );`
        );
      },
      (err) => reject(err),
      () => {
        console.log("✅ SQLite database initialized successfully.");
        resolve(true);
      }
    );
  });
};

// ===================================================
// 🔹 FARMER CRUD (same as your version)
// ===================================================

export const insertFarmer = (farmer) =>
  new Promise((resolve, reject) => {
    if (!db) return reject("Database not initialized");
    db.transaction((tx) => {
      tx.executeSql(
        `INSERT OR REPLACE INTO farmers (
          temp_id, nrc_number, first_name, last_name, phone_primary,
          phone_alternate, email, date_of_birth, gender, province,
          district, village, chiefdom, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);`,
        [
          farmer.temp_id,
          farmer.nrc_number,
          farmer.first_name,
          farmer.last_name,
          farmer.phone_primary,
          farmer.phone_alternate,
          farmer.email,
          farmer.date_of_birth,
          farmer.gender,
          farmer.province,
          farmer.district,
          farmer.village,
          farmer.chiefdom,
          farmer.latitude,
          farmer.longitude,
        ],
        (_, result) => resolve(result.insertId),
        (_, error) => reject(error)
      );
    });
  });

export const getLocalFarmers = () => {
    return new Promise((resolve, reject) => {
        db.transaction((tx) => {
            tx.executeSql(
                `SELECT * FROM farmers;`,
                [],
                (_, { rows: { _array } }) => resolve(_array),
                (_, error) => reject(error)
            );
        });
    });
};

export const getFarmerByTempId = (tempId) => {
    return new Promise((resolve, reject) => {
        db.transaction((tx) => {
            tx.executeSql(
                `SELECT * FROM farmers WHERE temp_id = ?;`,
                [tempId],
                (_, { rows: { _array } }) => resolve(_array[0]),
                (_, error) => reject(error)
            );
        });
    });
};

export const updateSyncStatus = (tempId, status, farmerId = null) => {
    return new Promise((resolve, reject) => {
        db.transaction((tx) => {
            tx.executeSql(
                `UPDATE farmers 
         SET sync_status = ?, farmer_id = ?, updated_at = CURRENT_TIMESTAMP
         WHERE temp_id = ?;`,
                [status, farmerId, tempId],
                (_, result) => {
                    console.log(`🔁 Farmer ${tempId} sync updated → ${status}`);
                    resolve(result);
                },
                (_, error) => reject(error)
            );
        });
    });
};

// ============================================
// 🔹 LAND & CROPS MANAGEMENT
// ============================================

export const insertLandParcel = (tempFarmerId, parcel) => {
    return new Promise((resolve, reject) => {
        db.transaction((tx) => {
            tx.executeSql(
                `INSERT INTO land_parcels (
          temp_farmer_id, parcel_id, total_area, ownership_type,
          land_type, soil_type, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);`,
                [
                    tempFarmerId,
                    parcel.parcel_id,
                    parcel.total_area,
                    parcel.ownership_type,
                    parcel.land_type,
                    parcel.soil_type,
                    parcel.latitude,
                    parcel.longitude,
                ],
                (_, result) => resolve(result.insertId),
                (_, error) => reject(error)
            );
        });
    });
};

export const insertCrop = (tempFarmerId, crop) => {
    return new Promise((resolve, reject) => {
        db.transaction((tx) => {
            tx.executeSql(
                `INSERT INTO crops (
          temp_farmer_id, crop_name, variety, area_allocated,
          planting_date, expected_harvest_date, irrigation_method,
          estimated_yield, season
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);`,
                [
                    tempFarmerId,
                    crop.crop_name,
                    crop.variety,
                    crop.area_allocated,
                    crop.planting_date,
                    crop.expected_harvest_date,
                    crop.irrigation_method,
                    crop.estimated_yield,
                    crop.season,
                ],
                (_, result) => resolve(result.insertId),
                (_, error) => reject(error)
            );
        });
    });
};

export const getLandParcels = (tempFarmerId) => {
    return new Promise((resolve, reject) => {
        db.transaction((tx) => {
            tx.executeSql(
                `SELECT * FROM land_parcels WHERE temp_farmer_id = ?;`,
                [tempFarmerId],
                (_, { rows: { _array } }) => resolve(_array),
                (_, error) => reject(error)
            );
        });
    });
};

export const getCrops = (tempFarmerId) => {
    return new Promise((resolve, reject) => {
        db.transaction((tx) => {
            tx.executeSql(
                `SELECT * FROM crops WHERE temp_farmer_id = ?;`,
                [tempFarmerId],
                (_, { rows: { _array } }) => resolve(_array),
                (_, error) => reject(error)
            );
        });
    });
};

// ============================================
// 🔹 STATS
// ============================================

export const getAllFarmersWithStats = () => {
    return new Promise((resolve, reject) => {
        db.transaction((tx) => {
            tx.executeSql(
                `SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN sync_status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN sync_status = 'synced' THEN 1 ELSE 0 END) as synced
         FROM farmers;`,
                [],
                (_, { rows: { _array } }) => resolve(_array[0]),
                (_, error) => reject(error)
            );
        });
    });
};
