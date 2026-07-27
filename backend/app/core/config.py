"""
Centralized application configuration.

All settings are read from environment variables (see .env.example). Nothing
in the codebase should read os.environ directly outside this module — every
other file imports `settings` from here so there is exactly one source of
truth for configuration.
"""
from functools import lru_cache
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_name: str = "CTF Insight AI"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    # --- Database ---
    database_url: str = Field(..., description="Async SQLAlchemy DSN (asyncpg)")
    database_url_sync: str = Field(..., description="Sync DSN, used by Alembic")

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- JWT ---
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    refresh_token_expire_days_remember_me: int = 90

    # --- Google OAuth ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    # --- Supabase Storage ---
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "writeups"

    # --- Email (Resend) ---
    resend_api_key: str = ""
    email_from: str = "CTF Insight AI <noreply@ctfinsight.ai>"

    # --- Stripe ---
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_premium_price_id: str = ""

    # --- AI Providers ---
    ai_default_provider: Literal["openai", "ollama"] = "openai"
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # --- Uploads ---
    max_upload_size_mb: int = 100
    allowed_upload_extensions: str = "md,pdf,txt,docx"

    # --- Rate limiting ---
    rate_limit_auth_per_minute: int = 5
    rate_limit_default_per_minute: int = 60

    @field_validator("allowed_upload_extensions")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.lower()

    @property
    def allowed_upload_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_upload_extensions.split(",") if ext.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — env is read once per process."""
    return Settings()


settings = get_settings()
