from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_api_key: SecretStr
    llm_base_url: str
    llm_model: str = "deepseek-flash"
    llm_temperature: float = Field(default=0.5, ge=0.0, le=2.0)
    llm_system: str = "你是一个讲技术很清楚的人。"