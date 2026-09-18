"""Demo 5: compare a fresh follow-up session with a validated handoff."""

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
from harness_demo.llm import Settings, call_text
from harness_demo.reporting import DemoReporter, active_reporter, report, test_summary

HANDOFF_PATH = "handoff.json"
HANDOFF_FIELDS = (
    "completed_work",
    "key_findings",
    "remaining_steps",
    "target_file",
    "verification_command",
)


def _session_a_prompt(workspace: Path, harness: bool) -> str:
    ticket = read_workspace_file(workspace, "DEMO_TICKET.md")
    source = read_workspace_file(workspace, "src/shipping.py")
    suffix = (
        "只返回 JSON 对象，且必须包含 completed_work、key_findings、remaining_steps、target_file、verification_command。"
        if harness
        else "分析任务，为下一位工程师写出简短调查结论；不要修改文件。"
    )
    return f"你是 Session A。只调查，不修改代码。{suffix}\n\n--- 工单 ---\n{ticket}\n\n--- 当前实现 ---\n{source}"


def _session_b_prompt(workspace: Path, handoff: dict[str, str] | None) -> str:
    ticket = read_workspace_file(workspace, "DEMO_TICKET.md")
    source = read_workspace_file(workspace, "src/shipping.py")
    handoff_section = ""
    if handoff is not None:
        handoff_section = "\n\n--- 来自 Session A 的已校验交接记录 ---\n" + json.dumps(
            handoff, ensure_ascii=False
        )
    return f"""你是 Session B。请完成运费升级并只在 <python> 和 </python> 之间返回完整 src/shipping.py。
不要修改测试；完成后不需要解释。你没有 Session A 的消息历史。{handoff_section}

--- 工单 ---
{ticket}

--- 当前实现 ---
{source}
"""


def parse_handoff(answer: str) -> dict[str, str]:
    if len(answer) > 8_000:
        raise ValueError("交接记录超过 8000 个字符")
    try:
        value = json.loads(answer)
    except json.JSONDecodeError as exc:
        raise ValueError("交接记录不是有效 JSON") from exc
    if not isinstance(value, dict) or set(value) != set(HANDOFF_FIELDS):
        raise ValueError("交接记录字段不完整或包含未知字段")
    handoff: dict[str, str] = {}
    for field in HANDOFF_FIELDS:
        item = value[field]
        if not isinstance(item, str) or not item.strip() or len(item) > 2_000:
            raise ValueError(f"交接记录字段无效: {field}")
        handoff[field] = item.strip()
    if handoff["target_file"] != "src/shipping.py":
        raise ValueError("交接记录目标文件不允许")
    if handoff["verification_command"] != "python -m pytest -q":
        raise ValueError("交接记录验证命令不允许")
    return handoff


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


def run(
    client: Any,
    settings: Settings,
    workspace: Path,
    harness: bool,
    reporter: DemoReporter | None = None,
) -> int:
    sink = active_reporter(reporter)
    report(
        sink,
        "input",
        "ready",
        "Session A 获得调查输入",
        "Session A 只调查，不修改代码。",
        evidence={
            "sources": ["DEMO_TICKET.md", "src/shipping.py"],
            "context_count": 2,
            "session": "A",
        },
        console_text="[INPUT] Session A：工单 + 初始实现",
    )
    first_answer = call_text(client, settings, _session_a_prompt(workspace, harness))
    report(
        sink,
        "llm",
        "completed",
        "Session A 完成调查",
        "该会话结束，不会传递消息历史。",
        evidence={"turn": 1, "call": True, "session": "A", "output": truncate(first_answer)},
        console_text="[LLM] Session A 调查完成",
    )
    handoff: dict[str, str] | None = None
    if harness:
        try:
            handoff = parse_handoff(first_answer)
        except ValueError as exc:
            report(
                sink,
                "handoff",
                "failed",
                "交接记录不可用",
                "Session A 未产生可安全恢复的结构化记录。",
                evidence={
                    "session": "A",
                    "handoff_available": False,
                    "handoff_valid": False,
                    "error": str(exc),
                },
                console_text=f"[HANDOFF] 无效: {exc}",
            )
            report(
                sink,
                "result",
                "handoff_error",
                "交接记录不可用",
                "系统不会从自由文本猜测状态。",
                evidence={
                    "calls": 1,
                    "test_runs": 0,
                    "final_test": "not_run",
                    "handoff_available": False,
                    "handoff_valid": False,
                    "task_outcome": "not_completed",
                    "capability_outcome": "handoff_error",
                    "stop_reason": "invalid_handoff",
                    "max_turns": settings.max_turns,
                },
                console_text="[RESULT] HANDOFF ERROR",
            )
            return 1
        (workspace / HANDOFF_PATH).write_text(
            json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        report(
            sink,
            "handoff",
            "completed",
            "保存结构化交接记录",
            "Session B 将读取经校验的 Session A 结论。",
            evidence={
                "session": "A→B",
                "handoff_available": True,
                "handoff_valid": True,
                "handoff_fields": list(HANDOFF_FIELDS),
                "path": HANDOFF_PATH,
            },
            console_text="[HANDOFF] 保存 handoff.json",
        )

    sources = ["DEMO_TICKET.md", "src/shipping.py"] + ([HANDOFF_PATH] if handoff else [])
    report(
        sink,
        "input",
        "ready",
        "Session B 获得继续任务输入",
        "包含经校验交接记录。" if handoff else "未提供 Session A 交接记录。",
        evidence={
            "sources": sources,
            "context_count": len(sources),
            "session": "B",
            "handoff_available": handoff is not None,
            "handoff_valid": handoff is not None,
        },
        console_text="[INPUT] Session B：新调用" + (" + handoff" if handoff else "（无 handoff）"),
    )
    answer = call_text(client, settings, _session_b_prompt(workspace, handoff))
    report(
        sink,
        "llm",
        "completed",
        "Session B 完成实现",
        "新的模型调用没有 Session A 消息历史。",
        evidence={"turn": 2, "call": True, "session": "B", "output": truncate(answer)},
        console_text="[LLM] Session B 生成实现",
    )
    content = extract_implementation(answer)
    write_implementation(workspace, content, "src/shipping.py")
    report(
        sink,
        "write",
        "completed",
        "写入继续后的实现",
        "Session B 更新 src/shipping.py。",
        evidence={
            "path": "src/shipping.py",
            "characters": len(content),
            "ok": True,
            "session": "B",
        },
        console_text="[WRITE] src/shipping.py",
    )
    final_test = run_tests(workspace, settings.timeout_seconds)
    _report_test(sink, final_test)
    files = changed_files(workspace)
    expected_files = ["src/shipping.py"] if not harness else [HANDOFF_PATH, "src/shipping.py"]
    passed = final_test.passed and files == expected_files
    report(
        sink,
        "result",
        "passed" if passed else "failed",
        "跨会话继续验证通过" if passed else "跨会话继续验证未通过",
        f"Session B 使用 {'有效交接记录' if handoff else '原始输入'} 完成后续工作。",
        evidence={
            "calls": 2,
            "test_runs": 1,
            "final_test": "passed" if final_test.passed else "failed",
            "modified_files": files,
            "diff": truncate(implementation_diff(workspace), 6_000),
            "scope_ok": files in (["src/shipping.py"], [HANDOFF_PATH, "src/shipping.py"]),
            "handoff_available": handoff is not None,
            "handoff_valid": handoff is not None,
            "task_outcome": "completed" if passed else "not_completed",
            "capability_outcome": "continued" if handoff else "no_handoff",
            "stop_reason": "session_b_completed",
            "max_turns": settings.max_turns,
        },
        console_text=f"[RESULT] {'PASS' if passed else 'FAIL'}",
    )
    return 0 if passed else 1
