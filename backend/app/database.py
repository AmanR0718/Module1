"""
backend/app/core/database.py
Zambian Farmer Support System — MongoDB (Motor) Async Database Connection
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError

from app.config import settings

# --------------------------------------------------
# Global Instances
# --------------------------------------------------
logger = logging.getLogger(__name__)
mongodb_client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


# --------------------------------------------------
# MongoDB Connection
# --------------------------------------------------
async def connect_to_mongo(retries: int = 5, delay: int = 3) -> None:
    """
    Connect to MongoDB with retry logic.
    """
    global mongodb_client, database

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Attempting MongoDB connection (Attempt {attempt}/{retries})...")

            mongodb_client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=5000,
            )

            # Test connection
            await mongodb_client.admin.command("ping")
            database = mongodb_client[settings.MONGODB_DB_NAME]

            logger.info(f"✅ Connected to MongoDB database: {settings.MONGODB_DB_NAME}")
            return

        except ServerSelectionTimeoutError as e:
            logger.warning(f"⚠️ MongoDB connection timed out: {e}")
        except PyMongoError as e:
            logger.error(f"❌ MongoDB connection error: {e}")
        except Exception as e:
            logger.exception(f"❌ Unexpected MongoDB connection error: {e}")

        if attempt < retries:
            await asyncio.sleep(delay)
        else:
            logger.critical("❌ Failed to connect to MongoDB after multiple retries.")
            raise


# --------------------------------------------------
# Close Connection
# --------------------------------------------------
async def close_mongo_connection() -> None:
    """
    Gracefully close MongoDB connection.
    """
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("✅ MongoDB connection closed.")


# --------------------------------------------------
# Accessor
# --------------------------------------------------
def get_database() -> AsyncIOMotorDatabase:
    """
    Return an active MongoDB database instance.
    """
    global database
    if database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return database


# --------------------------------------------------
# Index Creation
# --------------------------------------------------
async def create_indexes() -> None:
    """
    Create MongoDB indexes for optimized query performance.
    Automatically skips if indexes already exist.
    """
    try:
        db = get_database()

        # ----------------------
        # Users
        # ----------------------
        await db.users.create_index("email", unique=True)
        await db.users.create_index("role")
        await db.users.create_index("is_active")

        # ----------------------
        # Farmers
        # ----------------------
        await db.farmers.create_index("farmer_id", unique=True)
        await db.farmers.create_index("nrc_number", unique=True)
        await db.farmers.create_index([("personal_info.phone_primary", 1)])
        await db.farmers.create_index([
            ("address.province", 1),
            ("address.district", 1)
        ])
        await db.farmers.create_index("registration_status")
        await db.farmers.create_index("created_at")

        # ----------------------
        # Chiefs
        # ----------------------
        await db.chiefs.create_index([
            ("province", 1),
            ("district", 1)
        ])
        await db.chiefs.create_index("chief_name")
        await db.chiefs.create_index("is_active")

        # ----------------------
        # Inventory
        # ----------------------
        await db.inventory.create_index("item_id", unique=True)
        await db.inventory.create_index("category")
        await db.inventory.create_index("status")

        logger.info("✅ Database indexes verified/created successfully.")

    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}", exc_info=True)
        # Don't raise: index errors shouldn't block app startup


# --------------------------------------------------
# Utility (Optional)
# --------------------------------------------------
async def get_collection(name: str):
    """
    Helper to quickly access a collection by name.
    Example: coll = await get_collection('farmers')
    """
    db = get_database()
    return db[name]
