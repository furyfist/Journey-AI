import json

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_env: str = "development"
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    log_level: str = "INFO"

    # Stored as a raw string so pydantic-settings never tries to JSON-parse it
    # from the .env file. Use settings.cors_origins_list everywhere in the app.
    # Accepts: "http://localhost:3000"  OR  "http://a.com,http://b.com"  OR  '["http://a.com"]'
    cors_origins: str = "http://localhost:3000"

    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_anon_key: str = ""

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_fallback_model: str = "llama-4-scout"
    groq_max_tokens: int = 8192
    groq_temperature: float = 0.7

    unsplash_access_key: str = ""
    unsplash_secret_key: str = ""
    unsplash_base_url: str = "https://api.unsplash.com"

    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    overpass_api_url: str = "https://overpass-api.de/api/interpreter"
    geocoding_api_url: str = "https://geocoding-api.open-meteo.com/v1/search"

    @property
    def cors_origins_list(self) -> list[str]:
        v = self.cors_origins.strip()
        if v.startswith("["):
            return json.loads(v)
        return [o.strip() for o in v.split(",") if o.strip()]


settings = Settings()
