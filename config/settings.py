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


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        email_address=_env("EMAIL_ADDRESS"),
        email_password=_env("EMAIL_PASSWORD"),
        gemini_api_key=_env("GEMINI_API_KEY"),
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