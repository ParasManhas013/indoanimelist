from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from functools import lru_cache


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    APP_NAME: str = "IndoAList"
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/indoalist"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    LEADERBOARD_CACHE_TTL: int = 60  # seconds

    # JWT
    JWT_SECRET: str = "change-this-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Resend (Email)
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@indoalist.com"
    FROM_NAME: str = "IndoAList"

    # Cloudflare R2
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET_NAME: str = "indoalist-images"
    R2_PUBLIC_URL: str = "https://images.indoalist.com"

    # Bayesian ranking
    MIN_VOTES: int = 25  # minimum votes to qualify for leaderboard

    # Admin
    ADMIN_API_KEY: str = "change-this-admin-key-in-production"

    # Rate limiting
    REGISTER_RATE_LIMIT: str = "5/hour"
    RATE_ENDPOINT_LIMIT: str = "30/minute"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
