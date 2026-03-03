import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://trendsee_user:trendsee_password@db:5432/trendsee"
    sync_database_url: str = "postgresql://trendsee_user:trendsee_password@db:5432/trendsee"
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    
    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    
    # App
    secret_key: str = "your_secret_key_here_change_in_production"
    initial_balance: int = 1000
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Admin credentials
    admin_username: str = "admin"
    admin_password: str = "admin"
    
    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
