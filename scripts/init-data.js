// Run with: docker-compose exec mongodb mongosh -u admin -p password123 zambian_farmers < scripts/init-data.js

db = db.getSiblingDB('zambian_farmers');

print('📊 Loading sample data...');

// Sample Operators
db.users.insertMany([
    {
        email: "operator1@zambia.zm",
        full_name: "Joseph Banda",
        role: "operator",
        is_active: true,
        hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5PqjM4T.GdqYu",
        assigned_provinces: ["Central"],
        assigned_districts: ["Chibombo", "Kabwe"],
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        email: "operator2@zambia.zm",
        full_name: "Mary Mwanza",
        role: "operator",
        is_active: true,
        hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5PqjM4T.GdqYu",
        assigned_provinces: ["Eastern"],
        assigned_districts: ["Chipata"],
        created_at: new Date(),
        updated_at: new Date()
    }
]);

// More sample chiefs (add to existing)
db.chiefs.insertMany([
    // Southern Province
    {
        chief_name: "Chief Monze",
        tribal_affiliation: "Tonga",
        province: "Southern",
        district: "Monze",
        chiefdom: "Monze",
        phone: "+260-97-3456789",
        palace_location: { type: "Point", coordinates: [27.4833, -16.2833] }
    },
    // Western Province (Litunga)
    {
        chief_name: "Litunga Imwiko II",
        tribal_affiliation: "Lozi",
        province: "Western",
        district: "Mongu",
        chiefdom: "Barotseland",
        phone: "+260-97-4567890",
        palace_location: { type: "Point", coordinates: [23.1333, -15.2833] }
    },
    // Lusaka Province
    {
        chief_name: "Chief Chipepo",
        tribal_affiliation: "Lenje",
        province: "Lusaka",
        district: "Chongwe",
        chiefdom: "Chipepo",
        phone: "+260-97-5678901",
        palace_location: { type: "Point", coordinates: [28.6833, -15.3333] }
    }
]);

print('✅ Sample data loaded successfully!');