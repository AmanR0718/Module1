import * as SQLite from 'expo-sqlite';

const db = SQLite.openDatabase('zambian_farmers.db');

// Initialize database
export const initDatabase = () => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            // Farmers table
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

            // Land parcels table
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

            // Crops table
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

            // Documents table
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

            console.log('✅ Database initialized');
            resolve();
        }, reject);
    });
};

// Insert farmer
export const insertFarmer = (farmerData) => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            tx.executeSql(
                `INSERT INTO farmers (
          temp_id, nrc_number, first_name, last_name, phone_primary,
          phone_alternate, email, date_of_birth, gender, province,
          district, village, chiefdom, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [
                    farmerData.temp_id,
                    farmerData.nrc_number,
                    farmerData.first_name,
                    farmerData.last_name,
                    farmerData.phone_primary,
                    farmerData.phone_alternate,
                    farmerData.email,
                    farmerData.date_of_birth,
                    farmerData.gender,
                    farmerData.province,
                    farmerData.district,
                    farmerData.village,
                    farmerData.chiefdom,
                    farmerData.latitude,
                    farmerData.longitude
                ],
                (_, result) => resolve(result.insertId),
                (_, error) => reject(error)
            );
        });
    });
};

// Get all pending farmers
export const getPendingFarmers = () => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            tx.executeSql(
                `SELECT * FROM farmers WHERE sync_status = 'pending'`,
                [],
                (_, { rows: { _array } }) => resolve(_array),
                (_, error) => reject(error)
            );
        });
    });
};

// Get farmer by temp_id
export const getFarmerByTempId = (tempId) => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            tx.executeSql(
                `SELECT * FROM farmers WHERE temp_id = ?`,
                [tempId],
                (_, { rows: { _array } }) => resolve(_array[0]),
                (_, error) => reject(error)
            );
        });
    });
};

// Update sync status
export const updateSyncStatus = (tempId, status, farmerId = null) => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            tx.executeSql(
                `UPDATE farmers SET sync_status = ?, farmer_id = ?, updated_at = CURRENT_TIMESTAMP WHERE temp_id = ?`,
                [status, farmerId, tempId],
                (_, result) => resolve(result),
                (_, error) => reject(error)
            );
        });
    });
};

// Insert land parcel
export const insertLandParcel = (tempFarmerId, parcelData) => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            tx.executeSql(
                `INSERT INTO land_parcels (
          temp_farmer_id, parcel_id, total_area, ownership_type,
          land_type, soil_type, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
                [
                    tempFarmerId,
                    parcelData.parcel_id,
                    parcelData.total_area,
                    parcelData.ownership_type,
                    parcelData.land_type,
                    parcelData.soil_type,
                    parcelData.latitude,
                    parcelData.longitude
                ],
                (_, result) => resolve(result.insertId),
                (_, error) => reject(error)
            );
        });
    });
};

// Insert crop
export const insertCrop = (tempFarmerId, cropData) => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            tx.executeSql(
                `INSERT INTO crops (
          temp_farmer_id, crop_name, variety, area_allocated,
          planting_date, expected_harvest_date, irrigation_method,
          estimated_yield, season
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [
                    tempFarmerId,
                    cropData.crop_name,
                    cropData.variety,
                    cropData.area_allocated,
                    cropData.planting_date,
                    cropData.expected_harvest_date,
                    cropData.irrigation_method,
                    cropData.estimated_yield,
                    cropData.season
                ],
                (_, result) => resolve(result.insertId),
                (_, error) => reject(error)
            );
        });
    });
};

// Get land parcels for farmer
export const getLandParcels = (tempFarmerId) => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            tx.executeSql(
                `SELECT * FROM land_parcels WHERE temp_farmer_id = ?`,
                [tempFarmerId],
                (_, { rows: { _array } }) => resolve(_array),
                (_, error) => reject(error)
            );
        });
    });
};

// Get crops for farmer
export const getCrops = (tempFarmerId) => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            tx.executeSql(
                `SELECT * FROM crops WHERE temp_farmer_id = ?`,
                [tempFarmerId],
                (_, { rows: { _array } }) => resolve(_array),
                (_, error) => reject(error)
            );
        });
    });
};

// Get all farmers with counts
export const getAllFarmersWithStats = () => {
    return new Promise((resolve, reject) => {
        db.transaction(tx => {
            tx.executeSql(
                `SELECT 
          COUNT(*) as total,
          SUM(CASE WHEN sync_status = 'pending' THEN 1 ELSE 0 END) as pending,
          SUM(CASE WHEN sync_status = 'synced' THEN 1 ELSE 0 END) as synced
        FROM farmers`,
                [],
                (_, { rows: { _array } }) => resolve(_array[0]),
                (_, error) => reject(error)
            );
        });
    });
};
