"""Demo 3: compare one-shot generation with a test feedback loop."""

from __future__ import annotations

import ast
import re
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
from harness_demo.llm import Settings, call_text
from harness_demo.reporting import DemoReporter, active_reporter, report, test_summary

CODE_PATTERN = re.compile(r"<python>\s*(.*?)\s*</python>", re.DOTALL)


def extract_implementation(answer: str) -> str:
    match = CODE_PATTERN.search(answer)
    if not match:
        raise ValueError("模型输出缺少 <python>...</python> 完整文件标记")
    content = match.group(1).strip()
    if len(content) > 20_000:
        raise ValueError("模型生成的实现超过 20000 个字符")

    try:
        tree = ast.parse(content)
    except SyntaxError as exc:
        raise ValueError(f"模型生成的 Python 语法无效（第 {exc.lineno} 行）") from None
    if not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "calculate_shipping_fee"
        for node in tree.body
    ):
        raise ValueError("模型生成的文件缺少 calculate_shipping_fee")
    return f"{content}\n"


def _initial_prompt(workspace: Path) -> str:
    ticket = read_workspace_file(workspace, "DEMO_TICKET.md")
    implementation = read_workspace_file(workspace, "src/shipping.py")
    return f"""你是一名 Python 工程师。请根据工单修改给出的初始实现。
你看不到测试源码。请只在 <python> 和 </python> 之间返回完整的 src/shipping.py，
不要在标记外输出解释。

--- 工单 ---
{ticket}

--- 初始实现：src/shipping.py ---
{implementation}
"""


def _feedback_prompt(current: str, test_output: str) -> str:
    return f"""上一版实现没有通过验证。请根据测试失败摘要修复它。
你仍然看不到测试源码。只在 <python> 和 </python> 之间返回完整的 src/shipping.py。

--- 当前实现 ---
{current}

--- 测试失败摘要 ---
{test_output}
"""


def _write_answer(
    workspace: Path,
    answer: str,
    reporter: DemoReporter,
    turn: int,
) -> str:
    content = extract_implementation(answer)
    write_implementation(workspace, content, "src/shipping.py")
    report(
        reporter,
        "write",
        "completed",
        "写入生成实现",
        f"第 {turn} 版实现写入 src/shipping.py。",
        evidence={"turn": turn, "path": "src/shipping.py", "characters": len(content), "ok": True},
        console_text="[WRITE] src/shipping.py",
    )
    return content


def _print_result(
    workspace: Path,
    final_test_output: str,
    final_test_passed: bool,
    calls: int,
    test_runs: int,
    feedback_rounds: int,
    max_turns: int,
    stop_reason: str,
    reporter: DemoReporter,
) -> bool:
    files = changed_files(workspace)
    passed = final_test_passed and files == ["src/shipping.py"]
    diff = truncate(implementation_diff(workspace), 6_000)
    output = truncate(final_test_output, 4_000)
    passed_count, failed_count, failed_tests = test_summary(output)
    console = "\n".join(
        (
            f"[RESULT] LLM 调用次数: {calls}",
            f"[RESULT] 修改文件: {', '.join(files) if files else '(无)'}",
            "[DIFF]",
            diff,
            f"[TEST] {'PASS' if final_test_passed else 'FAIL'}",
            output,
            f"[RESULT] {'PASS' if passed else 'FAIL'}",
        )
    )
    report(
        reporter,
        "result",
        "passed" if passed else "failed",
        "反馈循环验证通过" if passed else "反馈循环验证未通过",
        f"{calls} 次生成，{test_runs} 次测试，{feedback_rounds} 次失败反馈。",
        evidence={
            "calls": calls,
            "test_runs": test_runs,
            "feedback_rounds": feedback_rounds,
            "final_test": "passed" if final_test_passed else "failed",
            "modified_files": files,
            "diff": diff,
            "command": "python -m pytest -q",
            "passed": final_test_passed,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "failed_tests": failed_tests,
            "output": output,
            "scope_ok": files == ["src/shipping.py"],
            "proposal_only": False,
            "max_turns": max_turns,
            "stop_reason": stop_reason,
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
    prompt = _initial_prompt(workspace)
    calls = 0
    test_runs = 0
    feedback_rounds = 0
    report(
        sink,
        "input",
        "ready",
        "模型获得任务与初始实现",
        "提供工单和 src/shipping.py；测试源码保持隐藏。",
        evidence={
            "sources": ["DEMO_TICKET.md", "src/shipping.py"],
            "context_count": 2,
        },
        console_text="[INPUT] 工单 + 初始实现（测试源码隐藏）",
    )

    if not harness:
        answer = call_text(client, settings, prompt)
        calls += 1
        report(
            sink,
            "llm",
            "completed",
            "模型完成单轮生成",
            "测试结果不会反馈给 PLAIN 模型。",
            evidence={"turn": 1, "call": True, "output": truncate(answer)},
            console_text="[LLM] 单轮生成（测试结果不会反馈给模型）",
        )
        _write_answer(workspace, answer, sink, 1)
        final_test = run_tests(workspace, settings.timeout_seconds)
        test_runs += 1
        _report_test(sink, final_test.output, final_test.returncode, final_test.passed, test_runs)
        passed = _print_result(
            workspace,
            final_test.output,
            final_test.passed,
            calls,
            test_runs,
            feedback_rounds,
            settings.max_turns,
            "single_generation",
            sink,
        )
        return 0 if passed else 1

    current = read_workspace_file(workspace, "src/shipping.py")
    final_test = None
    for turn in range(1, settings.max_turns + 1):
        answer = call_text(client, settings, prompt)
        calls += 1
        report(
            sink,
            "llm",
            "completed",
            "模型完成生成",
            f"完成第 {turn}/{settings.max_turns} 轮实现。",
            evidence={"turn": turn, "call": True, "output": truncate(answer)},
            console_text=f"[LLM] 生成轮次 {turn}/{settings.max_turns}",
        )
        current = _write_answer(workspace, answer, sink, turn)
        final_test = run_tests(workspace, settings.timeout_seconds)
        test_runs += 1
        _report_test(sink, final_test.output, final_test.returncode, final_test.passed, test_runs)

        if final_test.passed:
            break
        if turn < settings.max_turns:
            feedback_rounds += 1
            report(
                sink,
                "feedback",
                "sent",
                "失败摘要返回模型",
                f"第 {turn} 轮失败摘要成为第 {turn + 1} 轮输入。",
                evidence={
                    "target_turn": turn + 1,
                    "output": truncate(final_test.output, 4_000),
                },
                console_text="[FEEDBACK] 将精简失败摘要返回 LLM",
            )
            prompt = _feedback_prompt(current, truncate(final_test.output, 4_000))

    if final_test is None:
        raise ValueError("测试反馈循环未执行")
    passed = _print_result(
        workspace,
        final_test.output,
        final_test.passed,
        calls,
        test_runs,
        feedback_rounds,
        settings.max_turns,
        "test_passed" if final_test.passed else "max_turns",
        sink,
    )
    return 0 if passed else 1


def _report_test(
    reporter: DemoReporter,
    output: str,
    return_code: int,
    passed: bool,
    test_number: int,
) -> None:
    bounded_output = truncate(output, 4_000)
    passed_count, failed_count, failed_tests = test_summary(bounded_output)
    report(
        reporter,
        "test",
        "passed" if passed else "failed",
        "固定测试通过" if passed else "固定测试未通过",
        f"第 {test_number} 次测试：{passed_count} 项通过，{failed_count} 项失败。",
        evidence={
            "turn": test_number,
            "command": "python -m pytest -q",
            "return_code": return_code,
            "passed": passed,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "failed_tests": failed_tests,
            "output": bounded_output,
        },
        console_text=f"[TEST] {'PASS' if passed else 'FAIL'}\n{bounded_output}",
    )
