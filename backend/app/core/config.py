from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(alias="APP_NAME")
    app_env: str = Field(alias="APP_ENV")
    app_debug: bool = Field(alias="APP_DEBUG")
    api_v1_prefix: str = Field(alias="API_V1_PREFIX")
    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret_key: str = Field(min_length=32, alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()