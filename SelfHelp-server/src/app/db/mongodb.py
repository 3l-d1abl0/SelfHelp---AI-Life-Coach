from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from app.config import settings
from typing import Optional
from app.logger import logger

class MongoDB:
    client: MongoClient = None
    db = None

    @classmethod
    def connect_db(cls):
        """Create database connection and ensure database/collection exists."""

        logger.info("MONGO URL: %s", settings.MONGODB_URL)
        logger.info("MONGO DATABASE: %s", settings.MONGODB_DATABASE)
        logger.info("MONGO COLLECTION: %s", settings.MONGODB_MEETINGS_COLLECTION)
        try:
            # Connect to MongoDB
            cls.client = MongoClient(settings.MONGODB_URL, server_api=ServerApi('1'))
            logger.info(cls.client)
            # Get or create database
            cls.db = cls.client[settings.MONGODB_DATABASE]
            
            logger.info("--------------------------------")
            # Ensure the database exists by creating a collection if it doesn't exist
            cls.db.command('ping')
            
            # Create collection if it doesn't exist
            logger.info("--------------------------------")
            collection_names = cls.db.list_collection_names()
            if settings.MONGODB_MEETINGS_COLLECTION not in collection_names:
                logger.info("--------------------------------")
                cls.db.create_collection(settings.MONGODB_MEETINGS_COLLECTION)
                logger.info(f"Created collection: {settings.MONGODB_MEETINGS_COLLECTION}")
            
            # Create an index on created_at for better query performance
            collection = cls.db[settings.MONGODB_MEETINGS_COLLECTION]
            collection.create_index("created_at")
            
            logger.info(f"Connected to MongoDB database: {settings.MONGODB_DATABASE}")
            return cls.db
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise

    @classmethod
    def close_db(cls):
        """Close database connection."""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("MongoDB connection closed")

    @classmethod
    def get_db(cls):
        """Get database instance."""
        if cls.db is None:
            raise RuntimeError("Database is not connected. Call connect_db() first.")
        return cls.db

# Database instance
db = MongoDB()
