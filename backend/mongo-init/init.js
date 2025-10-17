// ============================================================
// MongoDB Initialization Script for Zambian Farmer System
// ============================================================

print('\n🌍 Initializing Zambian Farmer Database...\n');

const dbName = 'zambian_farmers';
const dbUser = 'admin';
const dbPassword = 'Admin123';

const db = db.getSiblingDB(dbName);

print(`📦 Using database: ${dbName}`);
print('-------------------------------------------');
print('📊 Creating collections...');

// ============================================================
// 🔹 COLLECTION CREATION
// ============================================================
function createCollectionSafe(name) {
  try {
    db.createCollection(name);
    print(`✅ Collection created: ${name}`);
  } catch (e) {
    if (e.codeName === 'NamespaceExists') {
      print(`⚠️  Collection already exists: ${name}`);
    } else {
      print(`❌ Error creating ${name}: ${e.message}`);
    }
  }
}

createCollectionSafe('farmers');
createCollectionSafe('users');
createCollectionSafe('chiefs');
createCollectionSafe('inventory');
createCollectionSafe('requests');
createCollectionSafe('sync_logs');

print('\n📍 Creating indexes...');
print('-------------------------------------------');

// ============================================================
// 🔹 INDEX CREATION
// ============================================================
function createIndexSafe(collection, keys, options = {}) {
  try {
    db[collection].createIndex(keys, options);
    print(`✅ Index created on ${collection}: ${JSON.stringify(keys)}`);
  } catch (e) {
    print(`⚠️  Index issue on ${collection}: ${e.message}`);
  }
}

// Farmers indexes
createIndexSafe('farmers', { farmer_id: 1 }, { unique: true });
createIndexSafe('farmers', { nrc_number: 1 }, { unique: true });
createIndexSafe('farmers', { 'personal_info.phone_primary': 1 });
createIndexSafe('farmers', { 'address.province': 1, 'address.district': 1 });
createIndexSafe('farmers', { registration_status: 1 });
createIndexSafe('farmers', { created_at: 1 });
createIndexSafe('farmers', { updated_at: 1 });
createIndexSafe('farmers', { created_by: 1 });
createIndexSafe('farmers', { 'farm_details.crops_grown': 1 });

// Users indexes
createIndexSafe('users', { email: 1 }, { unique: true });
createIndexSafe('users', { role: 1 });
createIndexSafe('users', { is_active: 1 });

// Chiefs indexes
createIndexSafe('chiefs', { province: 1, district: 1 });
createIndexSafe('chiefs', { chief_name: 1 });
createIndexSafe('chiefs', { is_active: 1 });

// Inventory indexes
createIndexSafe('inventory', { item_id: 1 }, { unique: true });
createIndexSafe('inventory', { category: 1 });
createIndexSafe('inventory', { status: 1 });

// Sync logs
createIndexSafe('sync_logs', { synced_at: 1 });
createIndexSafe('sync_logs', { user_id: 1 });

// ============================================================
// 🔹 ADMIN USER CREATION
// ============================================================
print('\n👤 Ensuring admin user exists...');
print('-------------------------------------------');

try {
  db.users.updateOne(
    { email: 'admin@test.com' },
    {
      $set: {
        email: 'admin@test.com',
        full_name: 'System Administrator',
        role: 'admin',
        is_active: true,
        hashed_password:
          '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5PqjM4T.GdqYu', // bcrypt('Admin@123')
        assigned_provinces: [],
        assigned_districts: [],
        created_at: new Date(),
        updated_at: new Date(),
      },
    },
    { upsert: true }
  );

  print('✅ Admin user created or already exists.');
} catch (e) {
  print(`⚠️  Error ensuring admin user: ${e.message}`);
}

// ============================================================
// 🔹 DATABASE USER AUTHENTICATION (for container access)
// ============================================================
print('\n🔐 Creating database user...');
print('-------------------------------------------');

try {
  db.createUser({
    user: dbUser,
    pwd: dbPassword,
    roles: [
      { role: 'readWrite', db: dbName },
      { role: 'dbAdmin', db: dbName },
    ],
  });
  print(`✅ Database user '${dbUser}' created successfully.`);
} catch (e) {
  print(`⚠️  Database user may already exist: ${e.message}`);
}

// ============================================================
// 🔹 FINAL STATUS
// ============================================================
print('\n🎉 Database initialization complete!');
print('✅ Collections: farmers, users, chiefs, inventory, requests, sync_logs');
print('✅ Admin user: admin@test.com');
print('✅ Database user: admin');
print('\n🚀 Zambian Farmer System MongoDB setup ready!\n');
