import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from app.config import settings
from app.logger import logger
from typing import Optional

class RedisManager:
    _pool: Optional[ConnectionPool] = None
    _client: Optional[redis.Redis] = None

    @classmethod
    def get_redis_pool(cls) -> ConnectionPool:
        """Get or create a Redis connection pool."""
        if cls._pool is None:
            cls._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_DB,
                decode_responses=True,
                max_connections=10
            )
            logger.info(f"Redis connection pool created for {settings.REDIS_URL} (DB: {settings.REDIS_DB})")
        return cls._pool

    @classmethod
    def get_redis_client(cls) -> redis.Redis:
        """Get or create a Redis client instance."""
        if cls._client is None or not cls._client.ping():
            pool = cls.get_redis_pool()
            cls._client = redis.Redis(connection_pool=pool)
        return cls._client

    @classmethod
    async def connect_redis(cls) -> None:
        """Initialize Redis connection and verify it works."""
        try:
            client = cls.get_redis_client()
            await client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            raise

    @classmethod
    async def close_redis(cls) -> None:
        """Close Redis connection pool."""
        if cls._client:
            await cls._client.close()
            cls._client = None
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None
            logger.info("Closed Redis connection pool")

# Redis instance
redis_manager = RedisManager()
