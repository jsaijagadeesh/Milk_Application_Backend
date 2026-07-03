from pydantic_settings import BaseSettings
from typing import List, Optional
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    
    # App
    app_name: str = os.getenv("APP_NAME", "Dairy App API")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./dairy_app.db")
    
    # CORS - Use hardcoded default (don't read from .env)
    allowed_origins: List[str] = ["*"]
    
    # Server
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
