"""Demo 6: compare stale knowledge with a versioned local authority source."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness_demo.common import (
    changed_files,
    implementation_diff,
    read_workspace_file,
    run_tests,
    truncate,
    write_implementation,
)
from harness_demo.demo_3_feedback import extract_implementation
from harness_demo.llm import Settings, call_text, create_response
from harness_demo.reporting import DemoReporter, active_reporter, report, test_summary

_POLICY_PATH = "provider/current-shipping-policy.json"
_CACHE_PATH = "docs/cached-shipping-policy.md"
_POLICY_FIELDS = {
    "source",
    "version",
    "effective_date",
    "domestic_base_fee_cents",
    "regular_free_shipping_threshold_cents",
    "member_free_shipping_threshold_cents",
    "international_flat_fee_cents",
}
TOOLS = [
    {
        "type": "function",
        "name": "get_current_shipping_policy",
        "description": "Read the local simulated provider's current policy with version metadata.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Replace src/shipping.py.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "enum": ["src/shipping.py"]},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "run_tests",
        "description": "Run the fixed pytest command.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
]


def load_current_policy(workspace: Path) -> dict[str, object]:
    try:
        raw = json.loads(read_workspace_file(workspace, _POLICY_PATH))
    except json.JSONDecodeError as exc:
        raise ValueError("当前提供方政策不是有效 JSON") from exc
    if not isinstance(raw, dict) or set(raw) != _POLICY_FIELDS:
        raise ValueError("当前提供方政策字段无效")
    required_strings = ("source", "version", "effective_date")
    required_numbers = tuple(_POLICY_FIELDS - set(required_strings))
    if any(not isinstance(raw[field], str) or not raw[field].strip() for field in required_strings):
        raise ValueError("当前提供方政策元数据无效")
    if any(not isinstance(raw[field], int) or raw[field] < 0 for field in required_numbers):
        raise ValueError("当前提供方政策规则无效")
    return raw


def _plain_prompt(workspace: Path) -> str:
    return f"""你是一名 Python 工程师。根据任务和下面明确标记为过期的缓存政策，
只在 <python> 和 </python> 之间返回完整 src/shipping.py。不要声称读取了当前 provider。

--- 工单 ---
{read_workspace_file(workspace, "DEMO_TICKET.md")}

--- 过期缓存 ---
{read_workspace_file(workspace, _CACHE_PATH)}

--- 初始实现 ---
{read_workspace_file(workspace, "src/shipping.py")}
"""


def _harness_prompt(workspace: Path) -> str:
    return f"""你是一名 Python 工程师。完成运费升级。必须先使用 get_current_shipping_policy
读取本地模拟 provider 的当前版本化政策，再写入 src/shipping.py 并运行固定测试。

--- 工单 ---
{read_workspace_file(workspace, "DEMO_TICKET.md")}

--- 初始实现 ---
{read_workspace_file(workspace, "src/shipping.py")}
"""


def _report_test(reporter: DemoReporter, result: object) -> None:
    output = truncate(result.output, 4_000)
    passed_count, failed_count, failed_tests = test_summary(output)
    report(
        reporter,
        "test",
        "passed" if result.passed else "failed",
        "固定测试通过" if result.passed else "固定测试未通过",
        f"{passed_count} 项通过，{failed_count} 项失败。",
        evidence={
            "command": "python -m pytest -q",
            "return_code": result.returncode,
            "passed": result.passed,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "failed_tests": failed_tests,
            "output": output,
        },
        console_text=f"[TEST] {'PASS' if result.passed else 'FAIL'}",
    )


def _tool_result(
    name: str,
    arguments: str,
    workspace: Path,
    settings: Settings,
    reporter: DemoReporter,
    state: dict[str, object],
) -> str:
    try:
        parsed = json.loads(arguments)
        if not isinstance(parsed, dict):
            raise TypeError("工具参数必须是 JSON 对象")
        if name == "get_current_shipping_policy":
            if parsed:
                raise ValueError("get_current_shipping_policy 不接受参数")
            policy = load_current_policy(workspace)
            state["grounding_used"] = True
            state["policy_version"] = policy["version"]
            state["effective_date"] = policy["effective_date"]
            result = {"ok": True, "policy": policy}
            report(
                reporter,
                "grounding",
                "completed",
                "取得当前提供方政策",
                "读取本地模拟 provider 的版本化只读政策。",
                evidence={
                    "tool_name": name,
                    "ok": True,
                    "schema_valid": True,
                    "permission_granted": True,
                    "executed": True,
                    "source_label": str(policy["source"]),
                    "policy_version": str(policy["version"]),
                    "effective_date": str(policy["effective_date"]),
                    "grounding_used": True,
                    "output": json.dumps(policy, ensure_ascii=False),
                },
                console_text=f"[GROUNDING] 当前政策 {policy['version']} / {policy['effective_date']}",
            )
        elif name == "write_file":
            path, content = parsed.get("path"), parsed.get("content")
            if path != "src/shipping.py" or not isinstance(content, str):
                raise ValueError("只允许完整写入 src/shipping.py")
            write_implementation(workspace, content, path)
            result = {"ok": True, "path": path}
            report(
                reporter,
                "write",
                "completed",
                "写入允许文件",
                "根据当前依据更新 src/shipping.py。",
                evidence={
                    "path": path,
                    "characters": len(content),
                    "ok": True,
                    "schema_valid": True,
                    "permission_granted": True,
                    "executed": True,
                },
                console_text="[WRITE] src/shipping.py",
            )
        elif name == "run_tests":
            if parsed:
                raise ValueError("run_tests 不接受参数")
            test_result = run_tests(workspace, settings.timeout_seconds)
            state["test_runs"] = int(state["test_runs"]) + 1
            _report_test(reporter, test_result)
            result = {"ok": test_result.passed, "output": test_result.output}
        else:
            raise ValueError(f"未知工具: {name}")
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
        state["rejected_requests"] = int(state["rejected_requests"]) + 1
        result = {"ok": False, "error": str(exc)}
        report(
            reporter,
            "tool",
            "rejected",
            "工具请求被拒绝",
            f"{name} 不符合当前依据工具约束。",
            evidence={
                "tool_name": name,
                "ok": False,
                "schema_valid": False,
                "permission_granted": False,
                "executed": False,
                "error": str(exc),
                "rejected_requests": state["rejected_requests"],
            },
            console_text=f"[TOOL] 拒绝 {name}: {exc}",
        )
    return json.dumps(result, ensure_ascii=False)


def _harness_run(
    client: Any, settings: Settings, workspace: Path, reporter: DemoReporter
) -> tuple[int, dict[str, object]]:
    inputs: list[Any] = [{"role": "user", "content": _harness_prompt(workspace)}]
    state: dict[str, object] = {
        "grounding_used": False,
        "policy_version": None,
        "effective_date": None,
        "test_runs": 0,
        "rejected_requests": 0,
    }
    for turn in range(1, settings.max_turns + 1):
        response = create_response(client, settings, input=inputs, tools=TOOLS)
        outputs = list(getattr(response, "output", []))
        calls = [item for item in outputs if getattr(item, "type", None) == "function_call"]
        if not calls:
            text = getattr(response, "output_text", "")
            report(
                reporter,
                "llm",
                "completed",
                "模型完成工具轮次",
                f"第 {turn} 轮返回最终说明。",
                evidence={
                    "turn": turn,
                    "call": True,
                    "output": truncate(text if isinstance(text, str) else ""),
                },
                console_text=f"[LLM] 工具轮次 {turn}/{settings.max_turns}",
            )
            return turn, state
        report(
            reporter,
            "llm",
            "tool_requested",
            "模型请求受控工具",
            f"第 {turn} 轮请求 {len(calls)} 项工具操作。",
            evidence={"turn": turn, "call": True},
            console_text=f"[LLM] 工具轮次 {turn}/{settings.max_turns}",
        )
        inputs.extend(outputs)
        for call in calls:
            value = _tool_result(call.name, call.arguments, workspace, settings, reporter, state)
            inputs.append(
                {"type": "function_call_output", "call_id": call.call_id, "output": value}
            )
    return settings.max_turns, state


def _result(
    workspace: Path,
    settings: Settings,
    reporter: DemoReporter,
    calls: int,
    state: dict[str, object],
    harness: bool,
) -> int:
    final_test = run_tests(workspace, settings.timeout_seconds)
    _report_test(reporter, final_test)
    files = changed_files(workspace)
    grounded = bool(state["grounding_used"])
    passed = final_test.passed and files == ["src/shipping.py"]
    grounding_error = harness and not grounded
    outcome = "grounding_error" if grounding_error else "passed" if passed else "failed"
    report(
        reporter,
        "result",
        outcome,
        "基于当前依据完成"
        if harness and grounded and passed
        else "当前依据未取得"
        if grounding_error
        else "依据演示验证未通过"
        if not passed
        else "基线依据结果",
        "本地模拟 provider 提供版本化事实，不代表联网服务。",
        evidence={
            "calls": calls,
            "test_runs": int(state["test_runs"]) + 1,
            "final_test": "passed" if final_test.passed else "failed",
            "modified_files": files,
            "diff": truncate(implementation_diff(workspace), 6_000),
            "scope_ok": files == ["src/shipping.py"],
            "grounding_used": grounded,
            "policy_version": state["policy_version"],
            "effective_date": state["effective_date"],
            "task_outcome": "completed" if passed else "not_completed",
            "capability_outcome": outcome,
            "rejected_requests": int(state["rejected_requests"]),
            "max_turns": settings.max_turns,
            "stop_reason": "model_completed" if calls < settings.max_turns else "max_turns",
        },
        console_text=f"[RESULT] {outcome.upper()}",
    )
    return 0 if passed and not grounding_error else 1


def run(
    client: Any,
    settings: Settings,
    workspace: Path,
    harness: bool,
    reporter: DemoReporter | None = None,
) -> int:
    sink = active_reporter(reporter)
    if not harness:
        report(
            sink,
            "input",
            "ready",
            "模型获得过期缓存",
            "PLAIN 没有当前提供方工具。",
            evidence={
                "sources": ["DEMO_TICKET.md", _CACHE_PATH, "src/shipping.py"],
                "context_count": 3,
                "source_label": "过期缓存",
            },
            console_text="[INPUT] 工单 + 过期缓存",
        )
        answer = call_text(client, settings, _plain_prompt(workspace))
        report(
            sink,
            "llm",
            "completed",
            "模型生成基于缓存的实现",
            "PLAIN 未取得当前 provider 依据。",
            evidence={"turn": 1, "call": True, "output": truncate(answer)},
            console_text="[LLM] 生成实现",
        )
        content = extract_implementation(answer)
        write_implementation(workspace, content, "src/shipping.py")
        report(
            sink,
            "write",
            "completed",
            "写入实现",
            "写入 src/shipping.py。",
            evidence={"path": "src/shipping.py", "characters": len(content), "ok": True},
            console_text="[WRITE] src/shipping.py",
        )
        return _result(
            workspace,
            settings,
            sink,
            1,
            {
                "grounding_used": False,
                "policy_version": None,
                "effective_date": None,
                "test_runs": 0,
                "rejected_requests": 0,
            },
            False,
        )
    report(
        sink,
        "input",
        "ready",
        "模型获得任务与依据工具",
        "HARNESS 可读取本地模拟 provider 的当前政策。",
        evidence={
            "sources": ["DEMO_TICKET.md", "src/shipping.py"],
            "context_count": 2,
            "source_label": "本地模拟 provider",
        },
        console_text="[INPUT] 工单 + 当前政策工具",
    )
    calls, state = _harness_run(client, settings, workspace, sink)
    return _result(workspace, settings, sink, calls, state, True)
