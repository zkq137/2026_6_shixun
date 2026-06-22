import os
from functools import cached_property

from dotenv import load_dotenv

load_dotenv()


class Settings:
    @property
    def app_name(self) -> str:
        return os.getenv("APP_NAME", "AI智能商城系统")

    @property
    def app_env(self) -> str:
        return os.getenv("APP_ENV", "development")

    @property
    def debug(self) -> bool:
        return os.getenv("DEBUG", "true").lower() in {"1", "true", "yes", "on"}

    @property
    def api_prefix(self) -> str:
        return os.getenv("API_PREFIX", "/api")

    @property
    def secret_key(self) -> str:
        return os.getenv("SECRET_KEY", "change-me-in-local-env")

    @property
    def access_token_expire_minutes(self) -> int:
        return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    @property
    def database_url(self) -> str:
        return os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://root:password@localhost:3306/ai_mall?charset=utf8mb4",
        )

    @property
    def redis_url(self) -> str:
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")

    @cached_property
    def cors_origins(self) -> list[str]:
        raw = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
        )
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def llm_provider(self) -> str:
        return os.getenv("LLM_PROVIDER", "openai_compatible")

    @property
    def llm_base_url(self) -> str:
        return os.getenv("LLM_BASE_URL", "")

    @property
    def llm_api_key(self) -> str:
        return os.getenv("LLM_API_KEY", "")

    @property
    def llm_model(self) -> str:
        return os.getenv("LLM_MODEL", "deepseek-chat")

    @property
    def llm_timeout_seconds(self) -> int:
        return int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))


settings = Settings()
