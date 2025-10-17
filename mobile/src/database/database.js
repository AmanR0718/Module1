import * as SQLite from 'expo-sqlite';
import { Alert } from 'react-native';

const DATABASE_NAME = 'zambian_farmers.db';
const DATABASE_VERSION = 1;

let database = null;

export const initializeDatabase = async () => {
    try {
        console.log('🗄️ Initializing SQLite database...');

        database = await SQLite.openDatabaseAsync(DATABASE_NAME);

        // Enable foreign keys
        await database.execAsync('PRAGMA foreign_keys = ON;');

        // Create tables
        await createTables();

        console.log('✅ Database initialized successfully');
        return database;

    } catch (error) {
        console.error('❌ Database initialization failed:', error);
        throw error;
    }
};

const createTables = async () => {
    const createTablesSQL = `
    -- Farmers table (main offline storage)
    CREATE TABLE IF NOT EXISTS farmers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      farmer_id TEXT UNIQUE,
      first_name TEXT NOT NULL,
      last_name TEXT NOT NULL,
      middle_name TEXT,
      date_of_birth TEXT NOT NULL,
      gender TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other')),
      marital_status TEXT CHECK (marital_status IN ('single', 'married', 'divorced', 'widowed')),
      nrc_number TEXT UNIQUE NOT NULL,
      phone_primary TEXT NOT NULL,
      phone_secondary TEXT,
      email TEXT,
      education_level TEXT,
      occupation TEXT,
      
      -- Address information
      province TEXT NOT NULL,
      district TEXT NOT NULL,
      constituency TEXT,
      ward TEXT,
      village TEXT,
      traditional_authority TEXT,
      postal_address TEXT,
      latitude REAL,
      longitude REAL,
      
      -- Farming information
      total_land_size REAL NOT NULL,
      farming_experience_years INTEGER,
      main_income_source TEXT,
      annual_income_range TEXT CHECK (annual_income_range IN ('below_5000', '5000_20000', '20000_50000', '50000_100000', 'above_100000')),
      
      -- Registration details
      registration_status TEXT DEFAULT 'pending' CHECK (registration_status IN ('pending', 'approved', 'rejected', 'incomplete')),
      registration_date TEXT NOT NULL,
      registered_by TEXT,
      
      -- QR Code information
      qr_code_generated INTEGER DEFAULT 0,
      qr_code_data TEXT,
      
      -- Sync status
      sync_status TEXT DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'failed')),
      last_sync_at TEXT,
      
      -- System fields
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      is_active INTEGER DEFAULT 1
    );

    -- Land holdings table
    CREATE TABLE IF NOT EXISTS land_holdings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      farmer_id INTEGER NOT NULL,
      plot_number TEXT,
      size_hectares REAL NOT NULL,
      land_type TEXT NOT NULL CHECK (land_type IN ('owned', 'rented', 'communal', 'leased')),
      title_deed_number TEXT,
      acquisition_date TEXT,
      soil_type TEXT,
      topography TEXT,
      water_source TEXT,
      irrigation_available INTEGER DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
    );

    -- Crops table
    CREATE TABLE IF NOT EXISTS crops (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      farmer_id INTEGER NOT NULL,
      crop_type TEXT NOT NULL,
      area_hectares REAL NOT NULL,
      planting_season TEXT NOT NULL CHECK (planting_season IN ('rainy', 'dry', 'both')),
      farming_method TEXT DEFAULT 'traditional' CHECK (farming_method IN ('traditional', 'conservation', 'organic', 'commercial')),
      expected_yield_tons REAL,
      market_destination TEXT,
      storage_facility TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
    );

    -- Documents table
    CREATE TABLE IF NOT EXISTS documents (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      farmer_id INTEGER NOT NULL,
      document_type TEXT NOT NULL,
      file_path TEXT NOT NULL,
      file_name TEXT NOT NULL,
      file_size INTEGER,
      upload_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      verified INTEGER DEFAULT 0,
      verified_by TEXT,
      verification_date TEXT,
      sync_status TEXT DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'failed')),
      FOREIGN KEY (farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
    );

    -- Chiefs table (reference data)
    CREATE TABLE IF NOT EXISTS chiefs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      chief_id TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      title TEXT NOT NULL,
      tribe TEXT NOT NULL,
      province TEXT NOT NULL,
      district TEXT NOT NULL,
      chiefdom TEXT NOT NULL,
      installation_date TEXT,
      palace TEXT,
      contact_person TEXT,
      phone_number TEXT,
      email TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    -- Sync log table
    CREATE TABLE IF NOT EXISTS sync_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      table_name TEXT NOT NULL,
      record_id INTEGER NOT NULL,
      action TEXT NOT NULL CHECK (action IN ('create', 'update', 'delete')),
      sync_status TEXT DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'failed')),
      error_message TEXT,
      attempts INTEGER DEFAULT 0,
      last_attempt_at TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    -- App settings table
    CREATE TABLE IF NOT EXISTS app_settings (
      key TEXT PRIMARY KEY,
      value TEXT,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_farmers_nrc ON farmers (nrc_number);
    CREATE INDEX IF NOT EXISTS idx_farmers_phone ON farmers (phone_primary);
    CREATE INDEX IF NOT EXISTS idx_farmers_province_district ON farmers (province, district);
    CREATE INDEX IF NOT EXISTS idx_farmers_sync_status ON farmers (sync_status);
    CREATE INDEX IF NOT EXISTS idx_farmers_registration_status ON farmers (registration_status);
    CREATE INDEX IF NOT EXISTS idx_land_holdings_farmer ON land_holdings (farmer_id);
    CREATE INDEX IF NOT EXISTS idx_crops_farmer ON crops (farmer_id);
    CREATE INDEX IF NOT EXISTS idx_documents_farmer ON documents (farmer_id);
    CREATE INDEX IF NOT EXISTS idx_documents_sync_status ON documents (sync_status);
    CREATE INDEX IF NOT EXISTS idx_chiefs_province_district ON chiefs (province, district);
    CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log (sync_status);
    CREATE INDEX IF NOT EXISTS idx_sync_log_table_record ON sync_log (table_name, record_id);
  `;

    await database.execAsync(createTablesSQL);
    console.log('✅ Database tables created successfully');
};

export const getDatabase = () => {
    if (!database) {
        throw new Error('Database not initialized. Call initializeDatabase first.');
    }
    return database;
};

// Database helper functions
export const executeQuery = async (sql, params = []) => {
    try {
        const db = getDatabase();
        const result = await db.runAsync(sql, params);
        return result;
    } catch (error) {
        console.error('Database query error:', error);
        throw error;
    }
};

export const executeSelect = async (sql, params = []) => {
    try {
        const db = getDatabase();
        const result = await db.getAllAsync(sql, params);
        return result;
    } catch (error) {
        console.error('Database select error:', error);
        throw error;
    }
};

export const executeSelectOne = async (sql, params = []) => {
    try {
        const db = getDatabase();
        const result = await db.getFirstAsync(sql, params);
        return result;
    } catch (error) {
        console.error('Database select one error:', error);
        throw error;
    }
};

// Transaction support
export const executeTransaction = async (operations) => {
    const db = getDatabase();

    try {
        await db.withTransactionAsync(async () => {
            for (const operation of operations) {
                await operation(db);
            }
        });
    } catch (error) {
        console.error('Transaction error:', error);
        throw error;
    }
};

// Database maintenance
export const clearDatabase = async () => {
    try {
        const db = getDatabase();

        // Clear all tables except settings and chiefs (reference data)
        await db.execAsync(`
      DELETE FROM sync_log;
      DELETE FROM documents;
      DELETE FROM crops;
      DELETE FROM land_holdings;
      DELETE FROM farmers;
    `);

        console.log('✅ Database cleared successfully');

    } catch (error) {
        console.error('❌ Error clearing database:', error);
        throw error;
    }
};

export const getDatabaseStats = async () => {
    try {
        const stats = {
            farmers: await executeSelectOne('SELECT COUNT(*) as count FROM farmers'),
            pendingSync: await executeSelectOne('SELECT COUNT(*) as count FROM farmers WHERE sync_status = "pending"'),
            chiefs: await executeSelectOne('SELECT COUNT(*) as count FROM chiefs'),
            documents: await executeSelectOne('SELECT COUNT(*) as count FROM documents'),
        };

        return {
            farmers: stats.farmers?.count || 0,
            pendingSync: stats.pendingSync?.count || 0,
            chiefs: stats.chiefs?.count || 0,
            documents: stats.documents?.count || 0,
        };

    } catch (error) {
        console.error('Error getting database stats:', error);
        return {
            farmers: 0,
            pendingSync: 0,
            chiefs: 0,
            documents: 0,
        };
    }
};

// Export for cleanup
export const closeDatabase = async () => {
    if (database) {
        await database.closeAsync();
        database = null;
        console.log('✅ Database connection closed');
    }
};
