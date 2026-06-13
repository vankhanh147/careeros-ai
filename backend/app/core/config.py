from functools import lru_cache
from os import getenv

from dotenv import load_dotenv

load_dotenv()


def _parse_cors_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def _required_env(name: str) -> str:
    value = getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _normalize_database_url(value: str) -> str:
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql://", 1)
    return value


class Settings:
    project_name: str = getenv("PROJECT_NAME", "CareerOS AI API")
    database_url: str = _normalize_database_url(_required_env("DATABASE_URL"))
    jwt_secret_key: str = _required_env("JWT_SECRET_KEY")
    jwt_algorithm: str = getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    allowed_origins: list[str] = _parse_cors_origins(
        getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
