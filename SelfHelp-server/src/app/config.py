from pydantic import Field, AnyHttpUrl, validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from functools import lru_cache
import os


class Settings(BaseSettings):

    # API Settings
    API_VERSION_STR: str = Field(default="/api/v1", description="Api version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment")
    
    # MongoDB Settings
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", description="MongoDB Url")
    MONGODB_DATABASE: str = Field(default="self-help", description="MongoDB Database")
    MONGODB_MEETINGS_COLLECTION: str = Field(default="meetings", description="MongoDB meetings collection")
    
    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    
    # Server
    PORT: int = Field(default=8000, description="Server port")
    RELOAD: bool = Field(default=True, description="Auto-reload on code changes")

    # API Keys
    # External API Keys (if needed for integration)
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None, description="ElevenLabs API key")
    ASSEMBLYAI_API_KEY: Optional[str] = Field(default=None, description="AssemblyAI API key")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description="GOOGLE API key")
    

    # BACKEND_CORS_ORIGINS: list = Field(
    #     default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    #     description="Allowed CORS origins"
    # )


    # CORS Settings
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ]

    
    class Config:
        env_file = ".env"
        env_file = os.path.join(os.path.dirname(__file__), "..","..","envs", ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
