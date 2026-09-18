"""Demo 2: compare a code proposal with bounded workspace tools."""

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
    workspace_passed,
    write_implementation,
)
from harness_demo.llm import Settings, call_text, create_response
from harness_demo.reporting import DemoReporter, active_reporter, report, test_summary

TOOLS = [
    {
        "type": "function",
        "name": "read_file",
        "description": "Read one UTF-8 text file from the synthetic demo workspace.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Workspace-relative file path."}
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Replace src/shipping.py with a complete UTF-8 Python implementation.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "enum": ["src/shipping.py"]},
                "content": {"type": "string", "description": "Complete Python file content."},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "run_tests",
        "description": "Run the fixture's fixed pytest verification command.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
]

CONTEXT_FILES = (
    "DEMO_TICKET.md",
    "AGENTS.md",
    "src/shipping.py",
    "tests/test_shipping.py",
    "docs/integration-notes.md",
    "docs/shipping-policy.md",
)


def _prompt(workspace: Path, harness: bool) -> str:
    sections = []
    for relative_path in CONTEXT_FILES:
        content = read_workspace_file(workspace, relative_path)
        sections.append(f"--- FILE: {relative_path} ---\n{content}\n--- END FILE ---")

    instruction = (
        "使用提供的工具检查工作区、修改允许的实现文件并运行测试。"
        "不要只描述方案；完成后简短报告工具验证结果。"
        if harness
        else "给出你建议的补丁或完整实现。你不能修改仓库或运行命令，不要声称已经完成这些操作。"
    )
    return f"""你是一名 Python 工程师。请处理下面的合成项目任务。
{instruction}

{chr(10).join(sections)}
"""


def _tool_result(
    name: str,
    arguments: str,
    workspace: Path,
    settings: Settings,
    reporter: DemoReporter | None = None,
) -> str:
    sink = active_reporter(reporter)
    try:
        parsed = json.loads(arguments)
        if not isinstance(parsed, dict):
            raise TypeError("工具参数必须是 JSON 对象")

        if name == "read_file":
            path = parsed.get("path")
            if not isinstance(path, str):
                raise ValueError("read_file.path 必须是字符串")
            content = truncate(read_workspace_file(workspace, path), 6_000)
            result: dict[str, Any] = {"ok": True, "path": path, "content": content}
            report(
                sink,
                "tool",
                "completed",
                "读取工作区文件",
                f"读取 {path}",
                evidence={
                    "tool_name": name,
                    "path": path,
                    "ok": True,
                    "schema_valid": True,
                    "permission_granted": True,
                    "executed": True,
                    "output": content,
                },
                console_text=f"[TOOL] read_file {path}",
            )
        elif name == "write_file":
            path = parsed.get("path")
            content = parsed.get("content")
            if not isinstance(path, str) or not isinstance(content, str):
                raise ValueError("write_file 需要字符串 path 和 content")
            write_implementation(workspace, content, path)
            result = {"ok": True, "path": path, "characters": len(content)}
            report(
                sink,
                "write",
                "completed",
                "写入允许文件",
                f"更新 {path}",
                evidence={
                    "path": path,
                    "characters": len(content),
                    "ok": True,
                    "schema_valid": True,
                    "permission_granted": True,
                    "executed": True,
                },
                console_text=f"[WRITE] {path}",
            )
        elif name == "run_tests":
            if parsed:
                raise ValueError("run_tests 不接受参数")
            test_result = run_tests(workspace, settings.timeout_seconds)
            summary = truncate(test_result.output, 4_000)
            passed_count, failed_count, failed_tests = test_summary(summary)
            result = {
                "ok": test_result.passed,
                "returncode": test_result.returncode,
                "output": summary,
            }
            report(
                sink,
                "test",
                "passed" if test_result.passed else "failed",
                "固定测试通过" if test_result.passed else "固定测试未通过",
                f"{passed_count} 项通过，{failed_count} 项失败。",
                evidence={
                    "command": "python -m pytest -q",
                    "return_code": test_result.returncode,
                    "passed": test_result.passed,
                    "passed_count": passed_count,
                    "failed_count": failed_count,
                    "failed_tests": failed_tests,
                    "output": summary,
                    "schema_valid": True,
                    "permission_granted": True,
                    "executed": True,
                },
                console_text=f"[TEST] {'PASS' if test_result.passed else 'FAIL'}",
            )
        else:
            raise ValueError(f"未知工具: {name}")
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
        result = {"ok": False, "error": str(exc)}
        report(
            sink,
            "tool",
            "rejected",
            "工具请求被拒绝",
            f"{name} 不符合受控工具约束。",
            evidence={
                "tool_name": name,
                "ok": False,
                "schema_valid": False,
                "permission_granted": False,
                "executed": False,
                "error": str(exc),
            },
            console_text=f"[TOOL] 拒绝 {name}: {exc}",
        )

    return json.dumps(result, ensure_ascii=False)


def _tool_loop(
    client: Any,
    settings: Settings,
    workspace: Path,
    prompt: str,
    reporter: DemoReporter,
) -> tuple[str, int]:
    input_items: list[Any] = [{"role": "user", "content": prompt}]
    final_text = ""

    for turn in range(1, settings.max_turns + 1):
        response = create_response(client, settings, input=input_items, tools=TOOLS)
        output_items = list(getattr(response, "output", []))
        tool_calls = [
            item for item in output_items if getattr(item, "type", None) == "function_call"
        ]

        if not tool_calls:
            text = getattr(response, "output_text", "")
            final_text = text.strip() if isinstance(text, str) else ""
            report(
                reporter,
                "llm",
                "completed",
                "模型完成工具轮次",
                f"第 {turn} 轮返回最终说明。",
                evidence={"turn": turn, "call": True, "output": truncate(final_text)},
                console_text=(
                    f"[LLM] 工具轮次 {turn}/{settings.max_turns}\n\n"
                    f"[LLM OUTPUT]\n{truncate(final_text)}"
                ),
            )
            return final_text, turn

        report(
            reporter,
            "llm",
            "tool_requested",
            "模型请求受控工具",
            f"第 {turn} 轮请求 {len(tool_calls)} 项工具操作。",
            evidence={"turn": turn, "call": True},
            console_text=f"[LLM] 工具轮次 {turn}/{settings.max_turns}",
        )

        # The Responses API requires all output items, including reasoning items,
        # to be returned with function outputs on the next request.
        input_items.extend(output_items)
        for call in tool_calls:
            result = _tool_result(call.name, call.arguments, workspace, settings, reporter)
            input_items.append(
                {"type": "function_call_output", "call_id": call.call_id, "output": result}
            )

    return final_text or "达到最大工具轮数，模型未返回最终文本。", settings.max_turns


def _print_workspace_result(
    workspace: Path,
    settings: Settings,
    turns: int,
    reporter: DemoReporter,
) -> bool:
    final_test = run_tests(workspace, settings.timeout_seconds)
    files = changed_files(workspace)
    passed = workspace_passed(workspace, final_test)
    diff = truncate(implementation_diff(workspace), 6_000)
    output = truncate(final_test.output, 4_000)
    passed_count, failed_count, failed_tests = test_summary(output)
    report(
        reporter,
        "test",
        "passed" if final_test.passed else "failed",
        "最终固定测试通过" if final_test.passed else "最终固定测试未通过",
        f"{passed_count} 项通过，{failed_count} 项失败。",
        evidence={
            "command": "python -m pytest -q",
            "return_code": final_test.returncode,
            "passed": final_test.passed,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "failed_tests": failed_tests,
            "output": output,
        },
    )
    console = "\n".join(
        (
            f"[RESULT] LLM 调用轮次: {turns}",
            f"[RESULT] 修改文件: {', '.join(files) if files else '(无)'}",
            "[DIFF]",
            diff,
            f"[TEST] {'PASS' if final_test.passed else 'FAIL'}",
            output,
            f"[RESULT] {'PASS' if passed else 'FAIL'}",
        )
    )
    report(
        reporter,
        "result",
        "passed" if passed else "failed",
        "实现验证通过" if passed else "实现验证未通过",
        f"修改 {len(files)} 个文件；最终测试{'通过' if final_test.passed else '未通过'}。",
        evidence={
            "calls": turns,
            "test_runs": 1,
            "feedback_rounds": 0,
            "final_test": "passed" if final_test.passed else "failed",
            "modified_files": files,
            "diff": diff,
            "command": "python -m pytest -q",
            "return_code": final_test.returncode,
            "passed": final_test.passed,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "failed_tests": failed_tests,
            "output": output,
            "scope_ok": files in ([], ["src/shipping.py"]),
            "proposal_only": False,
        },
        console_text="\n" + console,
    )
    return passed


def run(
    client: Any,
    settings: Settings,
    workspace: Path,
    harness: bool,
    reporter: DemoReporter | None = None,
) -> int:
    sink = active_reporter(reporter)
    prompt = _prompt(workspace, harness)
    report(
        sink,
        "input",
        "ready",
        "模型获得任务与项目输入",
        "提供任务、源码、测试和项目约束。",
        evidence={
            "sources": list(CONTEXT_FILES),
            "context_count": len(CONTEXT_FILES),
            "input_priority": ["任务", "项目规则", "工具定义"],
        },
        console_text="[INPUT] 任务 + 项目上下文",
    )
    if not harness:
        answer = call_text(client, settings, prompt)
        bounded_answer = truncate(answer)
        report(
            sink,
            "llm",
            "completed",
            "模型生成代码建议",
            "PLAIN 只能返回建议，不能修改或验证工作区。",
            evidence={"turn": 1, "call": True, "output": bounded_answer},
            console_text=(f"[LLM] 请求代码提案（无工作区工具）\n\n[LLM OUTPUT]\n{bounded_answer}"),
        )
        files = changed_files(workspace)
        report(
            sink,
            "result",
            "proposal",
            "仅生成代码建议",
            "未修改工作区，也未执行测试。",
            evidence={
                "calls": 1,
                "test_runs": 0,
                "feedback_rounds": 0,
                "final_test": "not_run",
                "modified_files": files,
                "workspace_unchanged": not files,
                "scope_ok": True,
                "proposal_only": True,
            },
            console_text=(
                f"\n[RESULT] 修改文件: {', '.join(files) if files else '(无)'}\n"
                "[RESULT] PROPOSAL ONLY — 未完成仓库修改或测试执行"
            ),
        )
        return 0 if not files else 1

    _, turns = _tool_loop(client, settings, workspace, prompt, sink)
    return 0 if _print_workspace_result(workspace, settings, turns, sink) else 1
