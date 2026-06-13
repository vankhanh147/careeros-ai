from functools import lru_cache
from os import getenv


def _parse_cors_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Settings:
    project_name: str = getenv("PROJECT_NAME", "CareerOS AI API")
    allowed_origins: list[str] = _parse_cors_origins(
        getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
