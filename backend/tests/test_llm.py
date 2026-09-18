from pathlib import Path

import pytest

from harness_demo.llm import (
    ConfigurationError,
    LLMCallError,
    Settings,
    call_text,
    load_settings,
)


def test_load_settings_requires_all_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        load_settings(tmp_path / "missing.env")


def test_load_settings_validates_positive_limits(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("OPENAI_MODEL", "demo-model")
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "0")

    with pytest.raises(ConfigurationError, match="OPENAI_TIMEOUT_SECONDS"):
        load_settings(tmp_path / "missing.env")


def test_llm_failure_is_sanitized() -> None:
    secret = "super-secret-key"

    class BrokenResponses:
        def create(self, **request: object) -> object:
            raise RuntimeError(f"Authorization: Bearer {secret}; request={request}")

    class BrokenClient:
        responses = BrokenResponses()

    settings = Settings(secret, "https://example.invalid/v1", "demo-model")
    with pytest.raises(LLMCallError) as captured:
        call_text(BrokenClient(), settings, "hello")

    assert secret not in str(captured.value)
    assert "Authorization" not in str(captured.value)
