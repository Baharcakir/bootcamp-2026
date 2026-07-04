from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Uygulama ayarları — kök dizindeki .env dosyasından okunur."""

    google_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    database_url: str = "sqlite:///./carpan.db"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
