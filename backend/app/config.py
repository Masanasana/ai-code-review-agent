"""
Application configuration.

This module loads configuration values from environment variables.

Sensitive values such as API keys should never be hardcoded
directly into the application source code.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Values are loaded from environment variables or the .env file.
    """

    # API key used to authenticate requests to Groq.
    groq_api_key: str

    # GitHub token used to authenticate GitHub API requests.
    #
    # This allows the application to access repository information
    # and post reviews back to pull requests.
    github_token: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create one settings object that can be imported throughout
# the application.
settings = Settings()