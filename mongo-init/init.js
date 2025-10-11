// MongoDB initialization script
db = db.getSiblingDB('zambian_farmers');

// Create collections
db.createCollection('farmers');
db.createCollection('users');
db.createCollection('chiefs');
db.createCollection('inventory');

// Create indexes
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

print('✅ MongoDB initialized successfully');

// Insert sample admin user (password: admin123)
db.users.insertOne({
    email: "admin@zambian-farmers.zm",
    full_name: "System Administrator",
    role: "admin",
    is_active: true,
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5PqjM4T.GdqYu",
    assigned_provinces: [],
    assigned_districts: [],
    created_at: new Date(),
    updated_at: new Date()
});

// Insert sample chiefs data (Central Province example)
db.chiefs.insertMany([
    {
        chief_name: "Chief Chitanda",
        tribal_affiliation: "Lenje",
        province: "Central",
        district: "Chibombo",
        chiefdom: "Chitanda",
        phone: "+260-97-1234567",
        email: "chief.chitanda@zambia.zm",
        jurisdiction_boundaries: {},
        palace_location: {
            type: "Point",
            coordinates: [28.4333, -14.7167]
        }
    },
    {
        chief_name: "Chief Liteta",
        tribal_affiliation: "Lenje",
        province: "Central",
        district: "Kabwe",
        chiefdom: "Liteta",
        phone: "+260-97-2345678",
        palace_location: {
            type: "Point",
            coordinates: [28.4467, -14.4464]
        }
    }
]);

print('✅ Sample data inserted');