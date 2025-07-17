from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/finance_coach_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI/ML APIs
    HUGGINGFACE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "finance-llm-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # ChromaDB
    CHROMA_DB_PATH: str = "./chroma_db"

    class Config:
        env_file = ".env"

settings = Settings()