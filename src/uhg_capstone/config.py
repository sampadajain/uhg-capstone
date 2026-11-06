from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    project_name: str = "uhg-capstone"
    database_url: str = os.getenv("POSTGRES_URL", "postgresql+psycopg://claims:claims@localhost:5432/claims")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    mailpit_smtp_host: str = os.getenv("MAILPIT_SMTP_HOST", "localhost")
    mailpit_smtp_port: int = int(os.getenv("MAILPIT_SMTP_PORT", "1025"))
    phoenix_collector_endpoint: str = os.getenv(
        "PHOENIX_COLLECTOR_ENDPOINT",
        "http://localhost:6006/api/v1/traces",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
