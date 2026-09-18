from __future__ import annotations

import json
from dataclasses import dataclass, field

from conftest import (
    CORRECT_IMPLEMENTATION,
    FakeClient,
    function_call,
    make_settings,
    text_response,
    tool_response,
)

from harness_demo.common import changed_files, prepare_workspace
from harness_demo.demo_4_control import run
from harness_demo.reporting import DemoEvent


@dataclass
class CollectReporter:
    events: list[DemoEvent] = field(default_factory=list)

    def emit(self, event: DemoEvent) -> None:
        self.events.append(event)


def test_demo_4_approved_harness_write_is_bounded() -> None:
    client = FakeClient(
        [
            tool_response(
                function_call(
                    "write_file",
                    json.dumps({"path": "src/shipping.py", "content": CORRECT_IMPLEMENTATION}),
                    "write",
                ),
                function_call("run_tests", "{}", "test"),
            ),
            text_response("完成。"),
        ]
    )
    workspace = prepare_workspace(4, True)
    reporter = CollectReporter()

    assert run(client, make_settings(), workspace, True, reporter, lambda *_: "approved") == 0
    assert changed_files(workspace) == ["src/shipping.py"]
    assert any(event.stage == "write" for event in reporter.events)


def test_demo_4_rejection_is_a_controlled_stop() -> None:
    client = FakeClient(
        [
            tool_response(
                function_call(
                    "write_file",
                    json.dumps({"path": "src/shipping.py", "content": CORRECT_IMPLEMENTATION}),
                    "write",
                )
            ),
        ]
    )
    workspace = prepare_workspace(4, True)
    reporter = CollectReporter()

    assert run(client, make_settings(), workspace, True, reporter, lambda *_: "rejected") == 0
    assert changed_files(workspace) == []
    assert reporter.events[-1].status == "controlled_stop"
    assert reporter.events[-1].evidence["capability_outcome"] == "controlled_stop"


def test_demo_4_plain_executes_without_approval() -> None:
    client = FakeClient(
        [
            tool_response(
                function_call(
                    "write_file",
                    json.dumps({"path": "src/shipping.py", "content": CORRECT_IMPLEMENTATION}),
                    "write",
                )
            ),
            text_response("完成。"),
        ]
    )
    workspace = prepare_workspace(4, False)
    reporter = CollectReporter()

    assert run(client, make_settings(), workspace, False, reporter) == 0
    assert not any(event.stage == "approval" for event in reporter.events)


def test_demo_4_timeout_is_a_controlled_stop() -> None:
    client = FakeClient(
        [
            tool_response(
                function_call(
                    "write_file",
                    json.dumps({"path": "src/shipping.py", "content": CORRECT_IMPLEMENTATION}),
                    "write",
                )
            ),
        ]
    )
    workspace = prepare_workspace(4, True)

    assert (
        run(client, make_settings(), workspace, True, approval_decider=lambda *_: "timed_out") == 0
    )


def test_demo_4_rejects_test_file_write_before_approval() -> None:
    client = FakeClient(
        [
            tool_response(
                function_call(
                    "write_file",
                    json.dumps({"path": "tests/test_shipping.py", "content": "x"}),
                    "bad",
                )
            ),
            text_response("停止。"),
        ]
    )
    workspace = prepare_workspace(4, True)
    reporter = CollectReporter()

    assert run(client, make_settings(), workspace, True, reporter, lambda *_: "approved") == 1
    assert changed_files(workspace) == []
    assert any(event.status == "rejected" for event in reporter.events)
