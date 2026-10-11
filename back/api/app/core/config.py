from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All sensitive values come from .env — required, fail-fast, no in-code defaults."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Nomoni API"
    database_url: str
    migration_database_url: str | None = None
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    cors_origins: str = "http://localhost:9000"
    system_user_email: str = "system@nomoni.com"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
