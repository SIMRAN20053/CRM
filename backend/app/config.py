"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """SmartReach AI application settings.

    Values are loaded from a `.env` file when present, with environment
    variables taking precedence.
    """

    APP_NAME: str = "SmartReach AI"
    DATABASE_URL: str = "sqlite+aiosqlite:///./smartreach.db"
    GEMINI_API_KEY: str = ""
    CHANNEL_SERVICE_URL: str = "http://localhost:8001"
    SECRET_KEY: str = "smartreach-dev-secret-key-2024"
    CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://smartreach-ai-seven.vercel.app",
    "https://smartreach-6cr2v83k2-simran20053s-projects.vercel.app",
]
CORS_ORIGINS: list[str] = ["*"]
class Config:
        env_file = ".env"


settings = Settings()
