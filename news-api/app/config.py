import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings
    """
    # MongoDB settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/")
    MONGO_DB: str = os.getenv("MONGO_DB", "news_db")
    MONGO_COLLECTION: str = "articles"

    # API settings
    API_TITLE: str = "Ojo Crítico News API"
    API_VERSION: str = "1.0.0"

    class Config:
        case_sensitive = True

settings = Settings()
