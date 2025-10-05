from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# MongoDB client
mongo_client: AsyncIOMotorClient = None
database = None

async def init_db():
    """
    Initialize database connection
    """
    global mongo_client, database
    mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
    database = mongo_client[settings.MONGO_DB]
    print(f"Connected to MongoDB: {settings.MONGO_DB}")

async def close_db():
    """
    Close database connection
    """
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("Closed MongoDB connection")

def get_database():
    """
    Get database instance
    """
    return database
