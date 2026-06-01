"""应用配置，通过 Pydantic Settings 校验环境变量。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置类。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str = "sqlite:///./baize.db"
    secret_key: str = "dev-secret-key"
    access_token_expire_minutes: int = 30


settings = Settings()
