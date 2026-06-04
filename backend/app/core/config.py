"""应用配置，通过 Pydantic Settings 校验环境变量。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置类。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # 数据库
    database_url: str = "sqlite:///./baize.db"

    # JWT 认证
    secret_key: str = "dev-secret-key"
    access_token_expire_minutes: int = 30

    # 首个管理员账户（系统初始化时自动创建，仅本地/开发环境使用）
    init_admin_email: str = ""
    init_admin_password: str = ""
    init_admin_username: str = ""

    # LLM 配置（兼容 OpenAI 协议的 API，如 DeepSeek、OpenAI 等）
    openai_api_key: str = ""
    openai_base_url: str = "https://api.deepseek.com"
    openai_model: str = "deepseek-v4-flash"

    # Embedding 配置
    embedding_provider: str = "local"  # "local"（sentence-transformers）或 "openai"
    embedding_model: str = "BAAI/bge-large-zh-v1.5"
    embedding_dim: int = 1024  # BGE-large-zh-v1.5 向量维度
    embedding_query_instruction: str = "为这个句子生成表示以用于检索相关文章："  # BGE 查询指令
    openai_embedding_model: str = "text-embedding-3-small"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    use_celery: bool = False  # False 时使用内联同步处理（开发模式）

    # Milvus Lite 存储
    milvus_db_file: str = "./milvus_data/baize.db"

    # CORS 允许的来源（逗号分隔，开发环境默认允许全部）
    cors_origins: str = "*"

    # 文件上传存储
    upload_dir: str = "./data/uploads"  # 上传文件落盘目录


settings = Settings()
