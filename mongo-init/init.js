db = db.getSiblingDB('zambian_farmers');

print('📊 Creating collections...');

// Create collections if they don't exist
try {
    db.createCollection('farmers');
    print('✅ farmers collection created');
} catch (e) {
    print('⚠️  farmers collection already exists');
}

try {
    db.createCollection('users');
    print('✅ users collection created');
} catch (e) {
    print('⚠️  users collection already exists');
}

try {
    db.createCollection('chiefs');
    print('✅ chiefs collection created');
} catch (e) {
    print('⚠️  chiefs collection already exists');
}

try {
    db.createCollection('inventory');
    print('✅ inventory collection created');
} catch (e) {
    print('⚠️  inventory collection already exists');
}

print('📍 Creating indexes...');

// Drop existing indexes first (optional)
try {
    db.farmers.collection.dropIndexes();
} catch (e) {
    print('No indexes to drop');
}

// Create new indexes
db.farmers.createIndex({ "farmer_id": 1 }, { unique: true });
db.farmers.createIndex({ "nrc_number": 1 }, { unique: true });
db.farmers.createIndex({ "personal_info.phone_primary": 1 });
db.farmers.createIndex({ "address.province": 1, "address.district": 1 });
db.farmers.createIndex({ "address.gps_coordinates": "2dsphere" });
db.farmers.createIndex({ "registration_status": 1 });
db.farmers.createIndex({ "created_at": 1 });

db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "role": 1 });

db.chiefs.createIndex({ "province": 1, "district": 1 });
db.chiefs.createIndex({ "chief_name": 1 });

print('✅ Indexes created');

print('👤 Creating admin user...');

// Insert admin user with proper password hash
db.users.updateOne(
    { email: "admin@zambian-farmers.zm" },
    {
        $set: {
            email: "admin@zambian-farmers.zm",
            full_name: "System Administrator",
            role: "admin",
            is_active: true,
            hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5PqjM4T.GdqYu",
            assigned_provinces: [],
            assigned_districts: [],
            created_at: new Date(),
            updated_at: new Date()
        }
    },
    { upsert: true }
);

print('✅ Admin user ready');

print('🎉 Database initialization complete!');