"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    groq_api_key: str

    # Optional for public-repository read access.
    # A token is still recommended because it gives GitHub API requests
    # a higher rate limit and is required if the app should post reviews.
    github_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
