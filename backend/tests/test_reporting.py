from __future__ import annotations

from dataclasses import dataclass, field

from conftest import (
    CORRECT_IMPLEMENTATION,
    FakeClient,
    make_settings,
    text_response,
)

from harness_demo.common import prepare_workspace
from harness_demo.demo_1_context import run as run_demo_1
from harness_demo.demo_3_feedback import run as run_demo_3
from harness_demo.reporting import DemoEvent
from harness_demo.web.models import RunSnapshot
from harness_demo.web.presentation import build_comparison, build_evidence
from harness_demo.web.runner import StoreReporter
from harness_demo.web.store import ExperimentStore


@dataclass
class CollectReporter:
    events: list[DemoEvent] = field(default_factory=list)

    def emit(self, event: DemoEvent) -> None:
        self.events.append(event)


def wrapped(content: str) -> str:
    return f"<python>\n{content}\n</python>"


def test_multiline_model_output_is_one_semantic_event() -> None:
    reporter = CollectReporter()
    workspace = prepare_workspace(1, False)
    answer = "第一行\n第二行\n第三行"

    assert (
        run_demo_1(
            FakeClient([text_response(answer)]),
            make_settings(),
            workspace,
            False,
            reporter,
        )
        == 0
    )

    assert [event.stage for event in reporter.events] == ["input", "llm", "result"]
    assert reporter.events[1].evidence["output"] == answer


def test_store_reporter_collects_prove_feedback_facts() -> None:
    workspace = prepare_workspace(3, True)
    initial = (workspace / "src/shipping.py").read_text(encoding="utf-8")
    store = ExperimentStore()
    experiment_id = store.create("prove")
    reporter = StoreReporter(store, experiment_id, "harness")

    assert (
        run_demo_3(
            FakeClient(
                [
                    text_response(wrapped(initial)),
                    text_response(wrapped(CORRECT_IMPLEMENTATION)),
                ]
            ),
            make_settings(max_turns=2),
            workspace,
            True,
            reporter,
        )
        == 0
    )

    snapshot = reporter.snapshot("completed", "passed")
    assert snapshot.calls == 2
    assert snapshot.test_runs == 2
    assert snapshot.feedback_rounds == 1
    assert snapshot.final_test == "passed"
    assert [event.stage for event in store.result(experiment_id).events].count("feedback") == 1


def test_comparison_copy_uses_objective_capability_facts() -> None:
    plain = RunSnapshot(
        status="completed",
        outcome="failed",
        calls=1,
        testRuns=1,
        finalTest="failed",
    )
    harness = RunSnapshot(
        status="completed",
        outcome="passed",
        calls=2,
        testRuns=2,
        feedbackRounds=1,
        finalTest="passed",
    )

    comparison = build_comparison("prove", plain, harness)

    assert comparison is not None
    assert "失败摘要" in comparison.observation
    assert "不是统计性 benchmark" in comparison.qualification
    assert comparison.metrics[-1].harness == "验证通过"


def test_comparison_does_not_treat_infrastructure_error_as_model_failure() -> None:
    comparison = build_comparison(
        "act",
        RunSnapshot(status="failed", outcome="infrastructure_error"),
        RunSnapshot(status="completed", outcome="passed"),
    )

    assert comparison is not None
    assert "不能直接比较" in comparison.observation
    assert comparison.metrics[0].plain == "实验运行异常"


def test_public_evidence_is_bounded_and_sanitized() -> None:
    evidence = build_evidence(
        "llm",
        {
            "call": True,
            "output": "OPENAI_API_KEY=secret\n" + "x" * 5_000,
        },
    )

    assert evidence.kind == "llm"
    assert evidence.output is not None
    assert "secret" not in evidence.output
    assert "已截断" in evidence.output


def test_comparison_uses_control_continue_and_ground_facts() -> None:
    control = build_comparison(
        "control",
        RunSnapshot(status="completed", outcome="passed", finalTest="passed"),
        RunSnapshot(
            status="completed",
            outcome="controlled_stop",
            approvalStatus="rejected",
            protectedActionExecuted=False,
            finalTest="failed",
        ),
    )
    ground = build_comparison(
        "ground",
        RunSnapshot(status="completed", outcome="failed", finalTest="failed"),
        RunSnapshot(
            status="completed",
            outcome="passed",
            groundingUsed=True,
            policyVersion="2026-09",
            effectiveDate="2026-09-01",
            finalTest="passed",
        ),
    )

    assert control is not None
    assert control.metrics[0].harness == "已拒绝"
    assert ground is not None
    assert ground.metrics[1].harness == "2026-09"
