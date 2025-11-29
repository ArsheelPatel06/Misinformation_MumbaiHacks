"""
Configuration management for DeepCheck MH
Loads environment variables and provides application settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    gemini_api_key: str
    openai_api_key: str
    news_api_key: Optional[str] = None
    
    # Reddit API (optional)
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "MisinfoDetector/1.0"
    
    # Twitter/X API (optional)
    twitter_bearer_token: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./deepcheck.db"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Agent Configuration
    monitoring_interval: int = 300  # seconds
    max_claims_per_cycle: int = 50
    enable_consensus_mode: bool = False  # Disabled until OpenAI has credits
    
    # AI Model Configuration
    gemini_model: str = "gemini-2.5-flash"
    openai_model: str = "gpt-4o-mini"
    
    # Crisis Keywords for filtering
    crisis_keywords: list[str] = [
        "pandemic", "covid", "outbreak", "epidemic",
        "war", "conflict", "invasion", "attack",
        "climate", "disaster", "earthquake", "flood", "hurricane",
        "emergency", "crisis", "breaking"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
