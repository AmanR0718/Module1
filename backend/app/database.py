from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    """Connect to MongoDB"""
    db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
    
    # Create indexes
    await create_indexes()
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db_instance.client:
        db_instance.client.close()
        print("❌ Closed MongoDB connection")

async def create_indexes():
    """Create database indexes for performance"""
    db = db_instance.db
    
    # Farmers collection indexes
    await db.farmers.create_index("farmer_id", unique=True)
    await db.farmers.create_index("nrc_number", unique=True)
    await db.farmers.create_index("personal_info.phone_primary")
    await db.farmers.create_index([("address.province", 1), ("address.district", 1)])
    await db.farmers.create_index([("address.gps_coordinates", "2dsphere")])
    await db.farmers.create_index("registration_status")
    await db.farmers.create_index("created_at")
    
    # Users collection indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")
    
    # Chiefs collection indexes
    await db.chiefs.create_index([("province", 1), ("district", 1)])
    await db.chiefs.create_index("chief_name")
    
    print("✅ Database indexes created")

def get_database():
    """Get database instance"""
    return db_instance.db
