from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

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

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    # Pinecone Settings
    pinecone_api_key: str
    pinecone_index_name: str = "rag-chatbot"
    pinecone_environment: str = "us-east-1"


    @property
    def allowed_origins_list(self) -> List[str]:
        """
        Convert comma-separated origins string to list and add Codespaces URLs dynamically.
        """
        # Start with origins from .env file
        origins = [origin.strip() for origin in self.allowed_origins.split(",")]
        
        # Check if running in GitHub Codespaces
        codespace_name = os.getenv("CODESPACE_NAME")
        
        if codespace_name:
            # Add Codespaces forwarded URLs automatically
            codespaces_origins = [
                f"https://{codespace_name}-5173.app.github.dev",  # Frontend (Vite default)
                f"https://{codespace_name}-3000.app.github.dev",  # Alternative frontend port
                f"https://{codespace_name}-8000.app.github.dev",  # Backend
            ]
            origins.extend(codespaces_origins)
            print(f"--Codespaces detected: {codespace_name}")
            print(f"--Added Codespaces URLs to CORS origins")
        
        # Add production URL if set in environment
        production_url = os.getenv("FRONTEND_URL")
        if production_url:
            origins.append(production_url)
            print(f"-Added production URL: {production_url}")
        
        print(f"Final CORS origins: {origins}")
        return origins

# Create global settings instance that other files can import
settings = Settings()