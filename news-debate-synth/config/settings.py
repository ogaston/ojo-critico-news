"""
Configuration settings for News Debate Synthesis AG2
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    
    # MongoDB Configuration
    mongo_uri: str = Field(
        default="mongodb://admin:admin123@localhost:27017/",
        env="MONGO_URI"
    )
    mongo_db: str = Field(default="news_db", env="MONGO_DB")
    
    # Application Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_debate_timeout: int = Field(default=300, env="MAX_DEBATE_TIMEOUT")
    batch_size: int = Field(default=10, env="BATCH_SIZE")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # AG2 Configuration
    max_rounds: int = Field(default=15, env="MAX_ROUNDS")
    agent_timeout: int = Field(default=60, env="AGENT_TIMEOUT")
    
    # Debate Configuration
    max_words_per_message: int = Field(default=180, env="MAX_WORDS_PER_MESSAGE")
    enable_spanish_translation: bool = Field(default=True, env="ENABLE_SPANISH_TRANSLATION")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings
