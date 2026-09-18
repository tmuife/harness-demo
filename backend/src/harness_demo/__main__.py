"""Command-line entry point for the live harness comparisons."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import Any

from harness_demo.common import prepare_workspace, print_header
from harness_demo.llm import (
    ConfigurationError,
    LLMCallError,
    Settings,
    create_client,
    load_settings,
)

DEMOS = {
    "1": ("项目上下文", "只增加只读项目上下文"),
    "2": ("受限工具行动", "只增加读/写/测试工具循环"),
    "3": ("测试反馈循环", "只增加测试失败反馈与再次修复"),
    "4": ("边界与审批", "只增加首次写入审批与更严格范围"),
    "5": ("跨会话状态", "只增加经校验的 Session A→B 交接记录"),
    "6": ("外部依据", "只增加当前版本化 provider 政策工具"),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="真实 LLM Harness 对照演示")
    parser.add_argument("demo", help="Demo 编号（1–6）或 list")
    parser.add_argument("--harness", action="store_true", help="启用当前 Demo 的目标能力")
    return parser


def print_demo_list() -> None:
    print("可用 Demo:")
    for number, (title, capability) in DEMOS.items():
        print(f"  {number}: {title} — {capability}")


def main(
    argv: Sequence[str] | None = None,
    *,
    settings: Settings | None = None,
    client: Any | None = None,
) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)

    if arguments.demo == "list":
        if arguments.harness:
            parser.error("list 命令不接受 --harness")
        print_demo_list()
        return 0

    if arguments.demo not in DEMOS:
        print(f"[ERROR] 未实现的 Demo: {arguments.demo}", file=sys.stderr)
        print_demo_list()
        return 2

    try:
        active_settings = settings or load_settings()
        active_client = client or create_client(active_settings)
        demo_number = int(arguments.demo)
        workspace = prepare_workspace(demo_number, arguments.harness)
        title, capability = DEMOS[arguments.demo]
        print_header(
            demo_number,
            title,
            arguments.harness,
            active_settings.model,
            capability,
        )

        if demo_number == 1:
            from harness_demo.demo_1_context import run
        elif demo_number == 2:
            from harness_demo.demo_2_tools import run
        elif demo_number == 3:
            from harness_demo.demo_3_feedback import run
        elif demo_number == 4:
            from harness_demo.demo_4_control import run
        elif demo_number == 5:
            from harness_demo.demo_5_continue import run
        else:
            from harness_demo.demo_6_ground import run

        return run(active_client, active_settings, workspace, arguments.harness)
    except (ConfigurationError, LLMCallError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
