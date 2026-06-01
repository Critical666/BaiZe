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

    # 首个管理员账户（系统初始化时自动创建，仅本地/开发环境使用）
    init_admin_email: str = "admin@baize.com"
    init_admin_password: str = "admin123"
    init_admin_username: str = "admin"


settings = Settings()
