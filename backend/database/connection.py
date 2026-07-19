from motor.motor_asyncio import AsyncIOMotorClient
from utils.logger import logger
from config import MONGO_URI, DATABASE_NAME

client = AsyncIOMotorClient(MONGO_URI)

logger.info(
    "Database connected successfully to host: %s", 
    client.host
)

db = client[DATABASE_NAME]
