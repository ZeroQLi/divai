from pathlib import Path
from pydantic_settings import BaseSettings

BACKEND_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    database_url: str = f"sqlite:///{BACKEND_ROOT / 'data.db'}"
    cors_origin: str = "http://localhost:3000"
    csv_path: str = str(BACKEND_ROOT / "housing_reschedule_with_english.csv")
    confidence_threshold: float = 0.7
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_prefix = ""

settings = Settings()