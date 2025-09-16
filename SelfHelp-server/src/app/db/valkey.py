from glide import GlideClient, NodeAddress
from glide.config import GlideClientConfiguration
from glide.exceptions import ClosingError, ConnectionError, TimeoutError
from app.config import settings
from app.logger import logger
from typing import Optional

class ValkeyManager:
    _client: Optional[GlideClient] = None

    @classmethod
    def _parse_valkey_url(cls) -> dict:
        """Parse Valkey URL and extract connection parameters."""
        
        config_params = {
            'addresses': [NodeAddress(
                host=settings.VALKEY_URL,
                port=settings.VALKEY_PORT
            )],
            'client_name': 'valkey-glide-client'
        }
        
        return config_params

    @classmethod
    def get_valkey_config(cls) -> GlideClientConfiguration:
        """Get or create a Valkey client configuration."""
        config_params = cls._parse_valkey_url()
        
        config = GlideClientConfiguration(
            addresses=config_params['addresses'],
            client_name=config_params.get('client_name'),
            request_timeout=5000,  # 5 seconds timeout
        )
        
        #Add credentials if present
        if 'credentials' in config_params:
            if 'username' in config_params['credentials']:
                config.credentials = {
                    'username': config_params['credentials']['username'],
                    'password': config_params['credentials']['password']
                }
            else:
                config.credentials = {
                    'password': config_params['credentials']['password']
                }
        
        return config

    @classmethod
    async def get_valkey_client(cls) -> GlideClient:
        """Get or create a Valkey client instance."""
        try:
            if cls._client is None:
                config = cls.get_valkey_config()
                print(config)
                cls._client = await GlideClient.create(config)
                logger.info(f"Valkey client created for {settings.VALKEY_URL}")
            return cls._client
        except Exception as e:
            logger.error(f"Unexpected Error while creating valkey client : {str(e)}")
            raise 

    @classmethod
    async def connect_valkey(cls) -> None:
        """Initialize Valkey connection and verify it works."""
        try:
            client = await cls.get_valkey_client()
            # Test connection with ping
            pong = await client.ping()
            if pong == b"PONG":
                logger.info("Successfully connected to Valkey")
            else:
                raise ConnectionError("Unexpected ping response")
        except (ClosingError, ConnectionError, TimeoutError) as e:
            logger.error(f"Error connecting to Valkey: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Valkey: {str(e)}")
            raise

    @classmethod
    async def close_valkey(cls) -> None:
        """Close Valkey client connection."""
        if cls._client:
            try:
                await cls._client.close()
                cls._client = None
                logger.info("Closed Valkey client connection")
            except Exception as e:
                logger.error(f"Error closing Valkey connection: {str(e)}")
                cls._client = None

    @classmethod
    async def health_check(cls) -> bool:
        """Check if Valkey connection is healthy."""
        try:
            if cls._client is None:
                return False
            pong = await cls._client.ping()
            return pong == b"PONG"
        except Exception:
            return False

    @classmethod
    async def reconnect_if_needed(cls) -> GlideClient:
        """Reconnect if the current connection is not healthy."""
        if not await cls.health_check():
            logger.warning("Valkey connection unhealthy, reconnecting...")
            await cls.close_valkey()
            return await cls.get_valkey_client()
        return cls._client

# Valkey instance
valkey_manager = ValkeyManager()