import json

from conftest import (
    CORRECT_IMPLEMENTATION,
    FakeClient,
    function_call,
    make_settings,
    text_response,
    tool_response,
)

from harness_demo.common import changed_files, prepare_workspace
from harness_demo.demo_2_tools import _tool_result, run


def test_demo_2_plain_leaves_workspace_unchanged() -> None:
    client = FakeClient([text_response("建议修改边界并增加国际订单分支。")])
    workspace = prepare_workspace(2, False)

    assert run(client, make_settings(), workspace, False) == 0
    assert changed_files(workspace) == []
    assert "tools" not in client.responses.calls[0]


def test_demo_2_harness_executes_bounded_tool_loop() -> None:
    first = tool_response(
        function_call(
            "write_file",
            json.dumps({"path": "src/shipping.py", "content": CORRECT_IMPLEMENTATION}),
            "call-write",
        ),
        function_call("run_tests", "{}", "call-tests"),
    )
    client = FakeClient([first, text_response("修改完成，测试通过。")])
    workspace = prepare_workspace(2, True)

    assert run(client, make_settings(), workspace, True) == 0
    assert changed_files(workspace) == ["src/shipping.py"]
    assert len(client.responses.calls) == 2
    second_input = client.responses.calls[1]["input"]
    assert any(
        item.get("type") == "function_call_output"
        for item in second_input
        if isinstance(item, dict)
    )


def test_demo_2_rejects_unknown_tool_and_write_path() -> None:
    workspace = prepare_workspace(2, True)
    settings = make_settings()

    unknown = json.loads(_tool_result("run_command", "{}", workspace, settings))
    escaped = json.loads(
        _tool_result(
            "write_file",
            json.dumps({"path": "../outside.py", "content": "x"}),
            workspace,
            settings,
        )
    )

    assert unknown["ok"] is False
    assert escaped["ok"] is False
