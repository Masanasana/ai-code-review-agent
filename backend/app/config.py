"""
Application configuration.

This module loads configuration values from environment variables.

Sensitive values such as API keys should never be hardcoded
directly into the application source code.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Values are automatically loaded from the .env file.
    """

    # API key used to authenticate requests to Groq.
    groq_api_key: str

    # Configuration for loading environment variables.
    #
    # extra="ignore" means that additional environment variables
    # will not cause validation errors.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create one settings object that can be imported throughout
# the application.
settings = Settings()