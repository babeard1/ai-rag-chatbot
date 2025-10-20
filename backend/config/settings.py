from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """App settings loaded from env variables."""

    #FastAPI Settings
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    #CORS Settings - Allowed URLs that can call the API
    # allowed_origins: List[str] = [
    #     "http://localhost:3000",
    #     "http://localhost:5173",
    #     "https://domainhere.app" #add later
    # ]

    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # Pinecone Settings
    pinecone_api_key: str
    pinecone_index_name: str = "rag-chatbot"
    pinecone_environment: str = "us-east-1"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins string to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
        
    #     # Validate required settings
    #     if not self.pinecone_api_key:
    #         raise ValueError("PINECONE_API_KEY is required in .env file")    

# Create global settings instance that other files can import
settings = Settings()