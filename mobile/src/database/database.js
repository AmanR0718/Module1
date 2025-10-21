// src/utils/database.js
import { Platform } from "react-native";

let SQLite; // lazy-loaded only when needed
if (Platform.OS !== "web") {
  try {
    SQLite = require("expo-sqlite");
  } catch (e) {
    console.warn("⚠️ Expo SQLite not available:", e.message);
  }
}


const DATABASE_NAME = "farmers.db";
let database = null;

/**
 * Initialize the SQLite database safely (mobile only).
 * On web, returns an in-memory mock implementation.
 */
export const initializeDatabase = async () => {
  try {
    console.log("🗄️ Initializing SQLite database...");

    // ✅ Web fallback: prevent crashes when running in browser
    if (Platform.OS === "web") {
      console.warn("⚠️ SQLite not supported on web — using mock in-memory DB.");
      database = {
        execAsync: async () => {},
        runAsync: async () => {},
        getAllAsync: async () => [],
        getFirstAsync: async () => null,
        withTransactionAsync: async (cb) => await cb(),
        closeAsync: async () => {},
      };
      return database;
    }

    // ✅ Mobile (Android/iOS)
    database = await SQLite.openDatabaseAsync(DATABASE_NAME);
    await database.execAsync("PRAGMA foreign_keys = ON;");
    await createTables();
    console.log("✅ Database initialized successfully");
    return database;
  } catch (error) {
    console.error("❌ Database initialization failed:", error);
    throw error;
  }
};

/**
 * Define schema and create all tables
 */
const createTables = async () => {
  const createTablesSQL = `
  CREATE TABLE IF NOT EXISTS farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id TEXT UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_name TEXT,
    date_of_birth TEXT NOT NULL,
    gender TEXT NOT NULL,
    marital_status TEXT,
    nrc_number TEXT UNIQUE NOT NULL,
    phone_primary TEXT NOT NULL,
    phone_secondary TEXT,
    email TEXT,
    education_level TEXT,
    occupation TEXT,
    province TEXT NOT NULL,
    district TEXT NOT NULL,
    constituency TEXT,
    ward TEXT,
    village TEXT,
    traditional_authority TEXT,
    postal_address TEXT,
    latitude REAL,
    longitude REAL,
    total_land_size REAL NOT NULL,
    farming_experience_years INTEGER,
    main_income_source TEXT,
    annual_income_range TEXT,
    registration_status TEXT DEFAULT 'pending',
    registration_date TEXT NOT NULL,
    registered_by TEXT,
    qr_code_generated INTEGER DEFAULT 0,
    qr_code_data TEXT,
    sync_status TEXT DEFAULT 'pending',
    last_sync_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
  );

  CREATE TABLE IF NOT EXISTS land_holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    plot_number TEXT,
    size_hectares REAL NOT NULL,
    land_type TEXT NOT NULL,
    title_deed_number TEXT,
    acquisition_date TEXT,
    soil_type TEXT,
    topography TEXT,
    water_source TEXT,
    irrigation_available INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    crop_type TEXT NOT NULL,
    area_hectares REAL NOT NULL,
    planting_season TEXT NOT NULL,
    farming_method TEXT DEFAULT 'traditional',
    expected_yield_tons REAL,
    market_destination TEXT,
    storage_facility TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
  );

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
    sync_status TEXT DEFAULT 'pending',
    FOREIGN KEY (farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
  );

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

  CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    sync_status TEXT DEFAULT 'pending',
    error_message TEXT,
    attempts INTEGER DEFAULT 0,
    last_attempt_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
  `;

  await database.execAsync(createTablesSQL);
  console.log("✅ Tables created successfully");
};

/**
 * Return the active database connection
 */
export const getDatabase = () => {
  if (!database) throw new Error("Database not initialized. Call initializeDatabase() first.");
  return database;
};

/**
 * Execute an INSERT/UPDATE/DELETE query
 */
export const executeQuery = async (sql, params = []) => {
  const db = getDatabase();
  try {
    return await db.runAsync(sql, params);
  } catch (error) {
    console.error("❌ Query error:", error);
    throw error;
  }
};

/**
 * Execute a SELECT query (multiple rows)
 */
export const executeSelect = async (sql, params = []) => {
  const db = getDatabase();
  try {
    return await db.getAllAsync(sql, params);
  } catch (error) {
    console.error("❌ Select error:", error);
    throw error;
  }
};

/**
 * Execute a SELECT query (single row)
 */
export const executeSelectOne = async (sql, params = []) => {
  const db = getDatabase();
  try {
    return await db.getFirstAsync(sql, params);
  } catch (error) {
    console.error("❌ SelectOne error:", error);
    throw error;
  }
};

/**
 * Run multiple operations in a transaction
 */
export const executeTransaction = async (operations) => {
  const db = getDatabase();
  try {
    await db.withTransactionAsync(async () => {
      for (const op of operations) await op(db);
    });
  } catch (error) {
    console.error("❌ Transaction error:", error);
    throw error;
  }
};

/**
 * Clear dynamic data (farmers, logs, etc.)
 */
export const clearDatabase = async () => {
  const db = getDatabase();
  try {
    await db.execAsync(`
      DELETE FROM sync_log;
      DELETE FROM documents;
      DELETE FROM crops;
      DELETE FROM land_holdings;
      DELETE FROM farmers;
    `);
    console.log("🧹 Database cleared successfully");
  } catch (error) {
    console.error("❌ Error clearing DB:", error);
  }
};

/**
 * Return quick stats for debug
 */
export const getDatabaseStats = async () => {
  try {
    return {
      farmers: (await executeSelectOne("SELECT COUNT(*) as c FROM farmers"))?.c || 0,
      pendingSync: (await executeSelectOne("SELECT COUNT(*) as c FROM farmers WHERE sync_status='pending'"))?.c || 0,
      chiefs: (await executeSelectOne("SELECT COUNT(*) as c FROM chiefs"))?.c || 0,
      documents: (await executeSelectOne("SELECT COUNT(*) as c FROM documents"))?.c || 0,
    };
  } catch (error) {
    console.error("Stats error:", error);
    return { farmers: 0, pendingSync: 0, chiefs: 0, documents: 0 };
  }
};

/**
 * Close connection (for cleanup)
 */
export const closeDatabase = async () => {
  if (database && Platform.OS !== "web") {
    await database.closeAsync();
    database = null;
    console.log("🔒 Database closed");
  }
};
