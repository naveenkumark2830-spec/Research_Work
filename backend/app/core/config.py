from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Assisted Interactive Hadoop Execution & Learning Simulator"
    SERVICE_NAME: str = "hadoop-ai-simulator-backend"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./hadoop_simulator.db"
    AI_PROVIDER: str = "mock"
    AI_MODEL: str = "gemini-2.5-flash"
    AI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    JARVIS_LLM_PROVIDER: str = "gemini"
    JARVIS_LLM_MODEL: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
