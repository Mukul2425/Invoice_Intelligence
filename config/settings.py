import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    email_address: str
    email_password: str
    gemini_api_key: str
    imap_server: str = "imap.gmail.com"
    imap_timeout_seconds: int = 20
    imap_retry_attempts: int = 3
    llm_timeout_seconds: int = 30
    llm_retry_attempts: int = 3


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if not raw:
        return default

    try:
        value = int(raw)
    except ValueError:
        return default

    return max(value, 1)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        email_address=_env("EMAIL_ADDRESS"),
        email_password=_env("EMAIL_PASSWORD"),
        gemini_api_key=_env("GEMINI_API_KEY"),
        imap_timeout_seconds=_env_int("IMAP_TIMEOUT_SECONDS", 20),
        imap_retry_attempts=_env_int("IMAP_RETRY_ATTEMPTS", 3),
        llm_timeout_seconds=_env_int("LLM_TIMEOUT_SECONDS", 30),
        llm_retry_attempts=_env_int("LLM_RETRY_ATTEMPTS", 3),
    )


def validate_startup_settings() -> None:
    settings = get_settings()

    missing = []
    if not settings.email_address:
        missing.append("EMAIL_ADDRESS")
    if not settings.email_password:
        missing.append("EMAIL_PASSWORD")
    if not settings.gemini_api_key:
        missing.append("GEMINI_API_KEY")

    if missing:
        fields = ", ".join(missing)
        raise ValueError(
            f"Missing required environment variables: {fields}. "
            "Set them in .env before running the pipeline."
        )
