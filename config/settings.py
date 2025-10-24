"""
Configuration settings for Financial AI Worker
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Financial AI Worker"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./financial_ai_worker.db"
    
    # Zerodha Configuration
    zerodha_api_key: Optional[str] = None
    zerodha_api_secret: Optional[str] = None
    zerodha_access_token: Optional[str] = None
    zerodha_redirect_url: str = "http://localhost:8000/zerodha/callback"
    
    # Trading 212 Configuration
    # Get your API key from: https://www.trading212.com/en/profile -> Settings -> API (Beta)
    trading212_api_key: Optional[str] = None
    trading212_api_secret: Optional[str] = None  # Not required for basic endpoints
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis (for caching)
    redis_url: str = "redis://localhost:6379"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/financial_ai_worker.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

