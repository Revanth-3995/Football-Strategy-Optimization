import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Football Analytics API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/football_analytics")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"

settings = Settings()