from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Voice Interview Coach"
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    knowledge_base_path: Path = Path("dataset/interview_knowledge_base.json")
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    max_questions: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
