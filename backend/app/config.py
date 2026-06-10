from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{BACKEND_ROOT / 'data.db'}"
    cors_origin: str = "http://localhost:3000"
    csv_path: str = str(BACKEND_ROOT / "housing_reschedule_with_english.csv")
    confidence_threshold: float = 0.7
    host: str = "0.0.0.0"
    port: int = 8000
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "google/gemma-4-31b-it"

settings = Settings()