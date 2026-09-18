"""OpenAI configuration and the small amount of shared API plumbing."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ConfigurationError(ValueError):
    """Raised when required local configuration is missing or invalid."""


class LLMCallError(RuntimeError):
    """A deliberately sanitized LLM request failure."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    timeout_seconds: int = 120
    max_turns: int = 4
    approval_timeout_seconds: int = 300


def _positive_int(name: str, default: int) -> int:
    raw_value = os.getenv(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} 必须是正整数") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} 必须是正整数")
    return value


def load_settings(env_path: Path | None = None) -> Settings:
    """Load required settings without ever including their values in errors."""
    load_dotenv(env_path or PROJECT_ROOT / ".env", override=False)

    required_names = ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL")
    missing = [name for name in required_names if not os.getenv(name, "").strip()]
    if missing:
        raise ConfigurationError(f"缺少必需环境变量: {', '.join(missing)}")

    return Settings(
        api_key=os.environ["OPENAI_API_KEY"].strip(),
        base_url=os.environ["OPENAI_BASE_URL"].strip(),
        model=os.environ["OPENAI_MODEL"].strip(),
        timeout_seconds=_positive_int("OPENAI_TIMEOUT_SECONDS", 120),
        max_turns=_positive_int("DEMO_MAX_TURNS", 4),
        approval_timeout_seconds=_positive_int("DEMO_APPROVAL_TIMEOUT_SECONDS", 300),
    )


def create_client(settings: Settings) -> OpenAI:
    return OpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=settings.timeout_seconds,
    )


def create_response(client: Any, settings: Settings, **request: Any) -> Any:
    """Make one Responses API call and expose only a safe error on failure."""
    try:
        return client.responses.create(model=settings.model, **request)
    except Exception as exc:  # noqa: BLE001 - sanitize every SDK/transport failure here
        raise LLMCallError(f"{type(exc).__name__}: LLM API 调用失败") from None


def call_text(client: Any, settings: Settings, prompt: str) -> str:
    response = create_response(client, settings, input=prompt)
    output_text = getattr(response, "output_text", "")
    if not isinstance(output_text, str) or not output_text.strip():
        raise LLMCallError("LLM API 未返回文本结果")
    return output_text.strip()
