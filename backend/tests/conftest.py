from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace
from typing import Any

from harness_demo.llm import Settings


class FakeResponses:
    def __init__(self, responses: Iterable[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def create(self, **request: Any) -> Any:
        self.calls.append(request)
        if not self._responses:
            raise AssertionError("Unexpected Responses API call")
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class FakeClient:
    def __init__(self, responses: Iterable[Any]) -> None:
        self.responses = FakeResponses(responses)


def text_response(text: str) -> SimpleNamespace:
    return SimpleNamespace(output_text=text, output=[])


def tool_response(*calls: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(output_text="", output=list(calls))


def function_call(name: str, arguments: str, call_id: str) -> SimpleNamespace:
    return SimpleNamespace(
        type="function_call",
        name=name,
        arguments=arguments,
        call_id=call_id,
    )


def make_settings(*, max_turns: int = 4) -> Settings:
    return Settings(
        api_key="test-key",
        base_url="https://example.invalid/v1",
        model="test-model",
        timeout_seconds=10,
        max_turns=max_turns,
    )


CORRECT_IMPLEMENTATION = '''"""Current shipping policy."""


def calculate_shipping_fee(
    subtotal_cents: int,
    destination: str,
    is_member: bool = False,
) -> int:
    """Return the shipping fee in cents."""
    if destination == "international":
        return 2000

    threshold = 3000 if is_member else 5000
    return 0 if subtotal_cents >= threshold else 800
'''
