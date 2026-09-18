"""Small typed reporting boundary shared by CLI and Web demo runs."""

from __future__ import annotations

import re
import select
import sys
from dataclasses import dataclass, field
from typing import Protocol

DemoStage = str


@dataclass(frozen=True)
class DemoEvent:
    """One meaningful demo operation and its bounded presentation evidence."""

    stage: DemoStage
    status: str
    title: str
    summary: str
    evidence: dict[str, object] = field(default_factory=dict)
    console_text: str = ""


class DemoReporter(Protocol):
    def emit(self, event: DemoEvent) -> None:
        """Publish one semantic operation."""


class ConsoleReporter:
    """Render semantic operations with the existing readable CLI labels."""

    def emit(self, event: DemoEvent) -> None:
        if event.console_text:
            print(event.console_text)

    def request_approval(self, action: str, scope: str, timeout_seconds: int) -> str:
        """Ask the CLI operator for one Control decision.

        EOF and a bounded wait are both treated as controlled stops.
        """
        print(f"[APPROVAL] {action}（范围: {scope}）批准？[y/N] ", end="", flush=True)
        try:
            ready, _, _ = select.select([sys.stdin], [], [], timeout_seconds)
        except (OSError, ValueError):
            ready = [sys.stdin]
        if not ready:
            return "timed_out"
        answer = sys.stdin.readline().strip().lower()
        if not answer:
            return "timed_out"
        return "approved" if answer in {"y", "yes", "是"} else "rejected"


def active_reporter(reporter: DemoReporter | None) -> DemoReporter:
    return reporter if reporter is not None else ConsoleReporter()


def request_approval(
    reporter: DemoReporter,
    action: str,
    scope: str,
    timeout_seconds: int,
) -> str:
    method = getattr(reporter, "request_approval", None)
    if not callable(method):
        raise TypeError("当前报告器不支持人工审批")
    decision = method(action, scope, timeout_seconds)
    if decision not in {"approved", "rejected", "timed_out"}:
        raise ValueError("审批结果无效")
    return decision


def report(
    reporter: DemoReporter,
    stage: DemoStage,
    status: str,
    title: str,
    summary: str,
    *,
    evidence: dict[str, object] | None = None,
    console_text: str = "",
) -> None:
    reporter.emit(
        DemoEvent(
            stage=stage,
            status=status,
            title=title,
            summary=summary,
            evidence=evidence or {},
            console_text=console_text,
        )
    )


def test_summary(output: str) -> tuple[int, int, list[str]]:
    """Extract small, presentation-only pytest facts from bounded output."""
    passed_matches = re.findall(r"(\d+) passed", output)
    failed_matches = re.findall(r"(\d+) failed", output)
    failed_tests = []
    for line in output.splitlines():
        if line.startswith("FAILED "):
            failed_tests.append(line.removeprefix("FAILED ").split(" - ", 1)[0])
    passed = int(passed_matches[-1]) if passed_matches else 0
    failed = int(failed_matches[-1]) if failed_matches else 0
    return passed, failed, failed_tests
