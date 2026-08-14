import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging

log = logging.getLogger("uvicorn")

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://spicDBManager:Polopolosolo123@cluster0.v0wyj6b.mongodb.net/")
DB_NAME = "fitai_biomechanics"

client = None
db = None

def get_database():
    global client, db
    if client is None:
        log.info(f"Connecting to MongoDB at {MONGO_URI}...")
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
    return db

def close_database_connection():
    global client
    if client is not None:
        client.close()
        log.info("MongoDB connection closed.")
