from conftest import FakeClient, make_settings, text_response

from harness_demo.common import changed_files, prepare_workspace
from harness_demo.demo_1_context import run


def test_demo_1_plain_sends_ticket_only() -> None:
    client = FakeClient([text_response("信息不足，建议先读取项目。")])
    workspace = prepare_workspace(1, False)

    assert run(client, make_settings(), workspace, False) == 0
    prompt = client.responses.calls[0]["input"]
    assert "运费规则升级" in prompt
    assert "FILE: src/shipping.py" not in prompt
    assert changed_files(workspace) == []


def test_demo_1_harness_includes_bounded_context() -> None:
    answer = (
        "修改 src/shipping.py；金额使用分。普通阈值 5000，会员阈值 3000，"
        "国际订单固定运费。保持函数签名，运行 python -m pytest -q。"
    )
    client = FakeClient([text_response(answer)])
    workspace = prepare_workspace(1, True)

    assert run(client, make_settings(), workspace, True) == 0
    prompt = client.responses.calls[0]["input"]
    for path in (
        "AGENTS.md",
        "src/shipping.py",
        "tests/test_shipping.py",
        "docs/integration-notes.md",
        "docs/shipping-policy.md",
    ):
        assert f"FILE: {path}" in prompt
    assert changed_files(workspace) == []
