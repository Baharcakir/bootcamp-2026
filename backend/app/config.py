from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Uygulama ayarları - kök dizindeki .env dosyasından okunur."""

    google_api_key: str | None = None
    gemini_model: str = "gemini-flash-latest"
    database_url: str = "sqlite:///./carpan.db"
    coach_memory_path: str = "./data/coach-checkpoints.sqlite3"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
