from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str = Field(default="", validation_alias="GITHUB_TOKEN")
    github_api_base_url: HttpUrl = Field(
        default="https://api.github.com", validation_alias="GITHUB_API_BASE_URL"
    )
    github_timeout_seconds: float = Field(default=20.0, validation_alias="GITHUB_TIMEOUT_SECONDS")
    allowed_repositories: str = Field(default="", validation_alias="ALLOWED_REPOSITORIES")
    max_patch_chars: int = Field(default=120_000, validation_alias="MAX_PATCH_CHARS")
    llm_analyzer_enabled: bool = Field(default=False, validation_alias="LLM_ANALYZER_ENABLED")
    llm_api_key: str = Field(default="", validation_alias="LLM_API_KEY")
    llm_api_base_url: HttpUrl = Field(
        default="https://api.openai.com/v1", validation_alias="LLM_API_BASE_URL"
    )
    llm_model: str = Field(default="gpt-4.1-mini", validation_alias="LLM_MODEL")
    llm_timeout_seconds: float = Field(default=30.0, validation_alias="LLM_TIMEOUT_SECONDS")
    llm_max_patch_chars: int = Field(default=40_000, validation_alias="LLM_MAX_PATCH_CHARS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def repository_allowlist(self) -> set[str]:
        return {
            item.strip().lower()
            for item in self.allowed_repositories.split(",")
            if item.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
