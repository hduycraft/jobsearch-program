import os
from dataclasses import dataclass, field
from functools import lru_cache


def _float_from_env(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        return float(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://careermatch:careermatch@localhost:5432/careermatch",
        )
    )
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "none"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "llama3.2:3b"))
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    )
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    llm_timeout_seconds: float = field(
        default_factory=lambda: _float_from_env("LLM_TIMEOUT_SECONDS", 20.0)
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
