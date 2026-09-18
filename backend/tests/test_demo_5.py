from __future__ import annotations

import json

from conftest import CORRECT_IMPLEMENTATION, FakeClient, make_settings, text_response

from harness_demo.common import changed_files, prepare_workspace
from harness_demo.demo_5_continue import HANDOFF_FIELDS, parse_handoff, run


def wrapped(content: str) -> str:
    return f"<python>\n{content}\n</python>"


def valid_handoff() -> str:
    return json.dumps(
        {
            "completed_work": "已检查初始实现。",
            "key_findings": "国际订单需要优先处理。",
            "remaining_steps": "更新实现并运行测试。",
            "target_file": "src/shipping.py",
            "verification_command": "python -m pytest -q",
        },
        ensure_ascii=False,
    )


def test_parse_handoff_requires_exact_safe_schema() -> None:
    assert set(parse_handoff(valid_handoff())) == set(HANDOFF_FIELDS)
    try:
        parse_handoff("{}")
    except ValueError as exc:
        assert "字段" in str(exc)
    else:
        raise AssertionError("missing handoff fields must fail")


def test_demo_5_harness_passes_valid_handoff_to_fresh_session() -> None:
    client = FakeClient(
        [text_response(valid_handoff()), text_response(wrapped(CORRECT_IMPLEMENTATION))]
    )
    workspace = prepare_workspace(5, True)

    assert run(client, make_settings(), workspace, True) == 0
    assert changed_files(workspace) == ["handoff.json", "src/shipping.py"]
    assert "已校验交接记录" in client.responses.calls[1]["input"]
    assert "你是 Session A" not in client.responses.calls[1]["input"]


def test_demo_5_stops_on_invalid_handoff_without_guessing() -> None:
    client = FakeClient([text_response("请继续处理国际订单。")])
    workspace = prepare_workspace(5, True)

    assert run(client, make_settings(), workspace, True) == 1
    assert changed_files(workspace) == []
    assert len(client.responses.calls) == 1


def test_demo_5_plain_session_b_does_not_receive_session_a_output() -> None:
    first = "Session A 的私有调查结论。"
    client = FakeClient([text_response(first), text_response(wrapped(CORRECT_IMPLEMENTATION))])
    workspace = prepare_workspace(5, False)

    assert run(client, make_settings(), workspace, False) == 0
    assert first not in client.responses.calls[1]["input"]
    assert changed_files(workspace) == ["src/shipping.py"]
