from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Database & Redis
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = Field(..., env="GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: str = Field(..., env="GITHUB_CLIENT_SECRET")
    GITHUB_REDIRECT_URI: str = Field(..., env="GITHUB_REDIRECT_URI")

    # WakaTime OAuth
    WAKATIME_CLIENT_ID: str = Field(..., env="WAKATIME_CLIENT_ID")
    WAKATIME_CLIENT_SECRET: str = Field(..., env="WAKATIME_CLIENT_SECRET")
    WAKATIME_REDIRECT_URI: str = Field(..., env="WAKATIME_REDIRECT_URI")

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()