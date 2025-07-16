from pydantic_settings import BaseSettings
from typing import Optional 

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/finance_coach_db"

    # Redis
    REDIS_URL:str="redis://localhost:6379"
    # aiml
    HUGGINGFACE_API_KEY:Optional[str]=None
    OPENAI_API_KEY:Optional[str]=None
    SECRET_KEY :str="finance-llm"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    BACKEND_CORS_ORIGINS:list=["http://localhost:3000"]

    class Config:
        env_file=".env"
    
settings=Settings()
