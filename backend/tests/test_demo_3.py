import pytest
from conftest import CORRECT_IMPLEMENTATION, FakeClient, make_settings, text_response

from harness_demo.common import changed_files, prepare_workspace
from harness_demo.demo_3_feedback import extract_implementation, run


def wrapped(content: str) -> str:
    return f"<python>\n{content}\n</python>"


def test_extract_implementation_requires_valid_complete_file() -> None:
    with pytest.raises(ValueError, match="完整文件标记"):
        extract_implementation("def calculate_shipping_fee(): pass")
    with pytest.raises(ValueError, match="语法无效"):
        extract_implementation("<python>def broken(</python>")
    with pytest.raises(ValueError, match="缺少 calculate_shipping_fee"):
        extract_implementation("<python>def other(): pass</python>")


def test_demo_3_plain_runs_once_without_feedback() -> None:
    client = FakeClient([text_response(wrapped(CORRECT_IMPLEMENTATION))])
    workspace = prepare_workspace(3, False)

    assert run(client, make_settings(), workspace, False) == 0
    assert len(client.responses.calls) == 1
    assert "tests/test_shipping.py" not in client.responses.calls[0]["input"]


def test_demo_3_harness_feeds_failure_back_and_repairs() -> None:
    initial = (prepare_workspace(3, True) / "src/shipping.py").read_text(encoding="utf-8")
    client = FakeClient(
        [
            text_response(wrapped(initial)),
            text_response(wrapped(CORRECT_IMPLEMENTATION)),
        ]
    )
    workspace = prepare_workspace(3, True)

    assert run(client, make_settings(max_turns=2), workspace, True) == 0
    assert len(client.responses.calls) == 2
    assert "测试失败摘要" in client.responses.calls[1]["input"]
    assert changed_files(workspace) == ["src/shipping.py"]


def test_demo_3_harness_stops_at_max_turns() -> None:
    workspace = prepare_workspace(3, True)
    initial = (workspace / "src/shipping.py").read_text(encoding="utf-8")
    client = FakeClient([text_response(wrapped(initial)), text_response(wrapped(initial))])

    assert run(client, make_settings(max_turns=2), workspace, True) == 1
    assert len(client.responses.calls) == 2
