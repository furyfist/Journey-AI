from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_env: str = "development"
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]

    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_anon_key: str = ""

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_fallback_model: str = "llama-4-scout"
    groq_max_tokens: int = 8192
    groq_temperature: float = 0.7

    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    overpass_api_url: str = "https://overpass-api.de/api/interpreter"
    geocoding_api_url: str = "https://geocoding-api.open-meteo.com/v1/search"


settings = Settings()
