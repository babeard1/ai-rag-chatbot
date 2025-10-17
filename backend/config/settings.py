from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """App settings loaded from env variables."""

    #FastAPI Settings
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    #CORS Settings - Allowed URLs that can call the API
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://domainhere.app" #add later
    ]

    class Config:
        env_file = ".env" # Tell pydantic to read from .env file

# Create global settings instance that other files can import
settings = Settings()