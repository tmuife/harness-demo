"""Demo 1: compare ticket-only analysis with project-aware analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness_demo.common import changed_files, read_workspace_file, truncate
from harness_demo.llm import Settings, call_text
from harness_demo.reporting import DemoReporter, active_reporter, report

CONTEXT_FILES = (
    "AGENTS.md",
    "src/shipping.py",
    "tests/test_shipping.py",
    "docs/integration-notes.md",
    "docs/shipping-policy.md",
)


def _prompt(workspace: Path, harness: bool) -> str:
    ticket = read_workspace_file(workspace, "DEMO_TICKET.md")
    prompt = f"""你是一名 Python 工程师。请分析下面的工单并给出简短、具体的处理方案。
不要声称已经修改文件或运行测试。

--- 工单 ---
{ticket}

输出应尽可能说明：目标文件、根因、需要遵守的接口/金额约束、配送规则和验证命令。
"""
    if not harness:
        return prompt

    sections = []
    for relative_path in CONTEXT_FILES:
        content = read_workspace_file(workspace, relative_path)
        sections.append(f"--- FILE: {relative_path} ---\n{content}\n--- END FILE ---")
    return f"{prompt}\n以下是 harness 收集的只读项目上下文：\n\n" + "\n\n".join(sections)


def _analysis_checks(answer: str) -> dict[str, bool]:
    lowered = answer.lower()
    return {
        "目标文件 src/shipping.py": "src/shipping.py" in lowered,
        "金额单位为分": "金额" in answer and ("分" in answer or "cent" in lowered),
        "普通用户阈值 5000": "5000" in answer,
        "会员阈值 3000": "3000" in answer,
        "国际订单规则": "国际" in answer or "international" in lowered,
        "公共 API 约束": "签名" in answer or "signature" in lowered,
        "验证命令 pytest": "pytest" in lowered,
    }


def run(
    client: Any,
    settings: Settings,
    workspace: Path,
    harness: bool,
    reporter: DemoReporter | None = None,
) -> int:
    sink = active_reporter(reporter)
    before = changed_files(workspace)
    sources = ["DEMO_TICKET.md", *CONTEXT_FILES] if harness else ["DEMO_TICKET.md"]
    input_label = "工单 + 只读项目上下文" if harness else "仅工单"
    report(
        sink,
        "input",
        "ready",
        "模型获得项目输入",
        input_label,
        evidence={
            "sources": sources,
            "context_count": len(sources),
            "input_priority": ["任务", "项目规则", "源码与测试"] if harness else ["任务"],
        },
        console_text=f"[INPUT] {input_label}",
    )
    answer = call_text(client, settings, _prompt(workspace, harness))
    bounded_answer = truncate(answer)
    report(
        sink,
        "llm",
        "completed",
        "模型完成分析",
        "分析已返回；检查其是否识别项目约束。",
        evidence={"turn": 1, "call": True, "output": bounded_answer},
        console_text=f"[LLM] 请求分析\n\n[LLM OUTPUT]\n{bounded_answer}",
    )

    checks = _analysis_checks(answer)
    check_lines = ["[CHECK] 提示性分析检查（不是 benchmark）"]
    for label, present in checks.items():
        marker = "✓" if present else "·"
        check_lines.append(f"  {marker} {label}")

    after = changed_files(workspace)
    unchanged = before == after == []
    result_lines = [
        *check_lines,
        f"[RESULT] 工作区未修改: {'YES' if unchanged else 'NO'}",
        "[RESULT] 本结果是分析，不是已完成的代码变更",
    ]
    report(
        sink,
        "result",
        "analysis",
        "分析完成",
        "完成项目约束检查；工作区按设计保持未修改。",
        evidence={
            "calls": 1,
            "test_runs": 0,
            "feedback_rounds": 0,
            "final_test": "not_run",
            "checks": checks,
            "workspace_unchanged": unchanged,
            "scope_ok": unchanged,
            "modified_files": after,
            "proposal_only": False,
        },
        console_text="\n" + "\n".join(result_lines),
    )
    return 0 if unchanged else 1
