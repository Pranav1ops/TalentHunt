from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://talenthunt:talenthunt_secret@localhost:5432/talenthunt"
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"
    API_PREFIX: str = "/api/v1"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
