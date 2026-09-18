"""Sequentially run demos and publish bounded semantic presentation events."""

from __future__ import annotations

from threading import Thread
from typing import cast

from harness_demo.common import prepare_workspace
from harness_demo.demo_1_context import run as run_demo_1
from harness_demo.demo_2_tools import run as run_demo_2
from harness_demo.demo_3_feedback import run as run_demo_3
from harness_demo.demo_4_control import run as run_demo_4
from harness_demo.demo_5_continue import run as run_demo_5
from harness_demo.demo_6_ground import run as run_demo_6
from harness_demo.llm import Settings, create_client, load_settings
from harness_demo.reporting import DemoEvent, DemoReporter
from harness_demo.web.catalog import CAPABILITY_TO_DEMO
from harness_demo.web.models import (
    EventEvidence,
    EventStage,
    FinalTestStatus,
    RunSide,
    RunSnapshot,
    RunStatus,
)
from harness_demo.web.presentation import build_evidence, sanitize_text
from harness_demo.web.store import ExperimentStore

_DEMO_RUNNERS = {
    1: run_demo_1,
    2: run_demo_2,
    3: run_demo_3,
    4: run_demo_4,
    5: run_demo_5,
    6: run_demo_6,
}


class StoreReporter(DemoReporter):
    """Store semantic events and collect objective facts for one run."""

    def __init__(self, store: ExperimentStore, experiment_id: str, side: RunSide) -> None:
        self._store = store
        self._experiment_id = experiment_id
        self._side = side
        self.calls = 0
        self.input_sources: list[str] = []
        self.modified_files: list[str] = []
        self.test_runs = 0
        self.feedback_rounds = 0
        self.final_test: FinalTestStatus = "unknown"
        self.checks: dict[str, bool] = {}
        self.workspace_unchanged: bool | None = None
        self.scope_ok: bool | None = None
        self.proposal_only = False
        self.max_turns: int | None = None
        self.stop_reason: str | None = None
        self.approval_status: str | None = None
        self.protected_action_executed: bool | None = None
        self.handoff_available: bool | None = None
        self.handoff_valid: bool | None = None
        self.policy_version: str | None = None
        self.effective_date: str | None = None
        self.grounding_used: bool | None = None
        self.task_outcome: str | None = None
        self.capability_outcome: str | None = None
        self.rejected_requests = 0
        self.pending_result: DemoEvent | None = None

    def emit(self, event: DemoEvent) -> None:
        stage = _event_stage(event.stage)
        evidence = build_evidence(stage, event.evidence)
        self._collect(stage, evidence)
        if stage == "result":
            self.pending_result = event
            return
        self._store.emit(
            self._experiment_id,
            self._side,
            stage,
            event.status,
            sanitize_text(event.title),
            sanitize_text(event.summary),
            evidence,
        )

    def snapshot(self, status: RunStatus, outcome: str) -> RunSnapshot:
        return RunSnapshot(
            status=status,
            outcome=outcome,
            calls=self.calls,
            input_sources=self.input_sources,
            modified_files=self.modified_files,
            test_runs=self.test_runs,
            feedback_rounds=self.feedback_rounds,
            final_test=self.final_test,
            checks=self.checks,
            workspace_unchanged=self.workspace_unchanged,
            scope_ok=self.scope_ok,
            proposal_only=self.proposal_only,
            max_turns=self.max_turns,
            stop_reason=self.stop_reason,
            approval_status=self.approval_status,
            protected_action_executed=self.protected_action_executed,
            handoff_available=self.handoff_available,
            handoff_valid=self.handoff_valid,
            policy_version=self.policy_version,
            effective_date=self.effective_date,
            grounding_used=self.grounding_used,
            task_outcome=self.task_outcome,
            capability_outcome=self.capability_outcome,
            rejected_requests=self.rejected_requests,
        )

    def request_approval(self, action: str, scope: str, timeout_seconds: int) -> str:
        approval_id = self._store.open_approval(self._experiment_id, self._side, action, scope)
        self._store.emit(
            self._experiment_id,
            self._side,
            "approval",
            "pending",
            "等待人工审批",
            "首次受保护写入需要确认。",
            {
                "approval_id": approval_id,
                "action": action,
                "scope": scope,
                "approval_status": "pending",
            },
        )
        decision = self._store.wait_for_approval(approval_id, timeout_seconds)
        self._store.emit(
            self._experiment_id,
            self._side,
            "approval",
            decision,
            {"approved": "审批已批准", "rejected": "审批已拒绝", "timed_out": "审批等待超时"}[
                decision
            ],
            "受保护动作将按该决定继续或停止。",
            {
                "approval_id": approval_id,
                "action": action,
                "scope": scope,
                "approval_status": decision,
            },
        )
        return decision

    def _collect(self, stage: EventStage, evidence: EventEvidence) -> None:
        if stage == "input":
            self.input_sources = list(evidence.sources)
        if stage == "llm" and evidence.call:
            self.calls += 1
        if stage == "write" and evidence.path and evidence.path not in self.modified_files:
            self.modified_files.append(evidence.path)
        if stage == "test":
            self.test_runs += 1
            if evidence.passed is not None:
                self.final_test = "passed" if evidence.passed else "failed"
        if stage == "feedback":
            self.feedback_rounds += 1
        if stage == "tool" and evidence.ok is False:
            self.rejected_requests += 1
        if stage == "result":
            self.calls = max(self.calls, evidence.calls or 0)
            self.test_runs = max(self.test_runs, evidence.test_runs or 0)
            self.feedback_rounds = max(self.feedback_rounds, evidence.feedback_rounds or 0)
            self.final_test = evidence.final_test or self.final_test
            self.modified_files = list(evidence.modified_files or self.modified_files)
            self.checks = dict(evidence.checks)
            self.workspace_unchanged = evidence.workspace_unchanged
            self.scope_ok = evidence.scope_ok
            self.proposal_only = bool(evidence.proposal_only)
            self.max_turns = evidence.max_turns
            self.stop_reason = evidence.stop_reason
            self.approval_status = evidence.approval_status
            self.protected_action_executed = evidence.protected_action_executed
            self.handoff_available = evidence.handoff_available
            self.handoff_valid = evidence.handoff_valid
            self.policy_version = evidence.policy_version
            self.effective_date = evidence.effective_date
            self.grounding_used = evidence.grounding_used
            self.task_outcome = evidence.task_outcome
            self.capability_outcome = evidence.capability_outcome
            self.rejected_requests = max(self.rejected_requests, evidence.rejected_requests or 0)


def start_experiment(store: ExperimentStore, experiment_id: str, capability_id: str) -> None:
    thread = Thread(
        target=_run_experiment,
        args=(store, experiment_id, capability_id),
        name=f"harness-{experiment_id}",
        daemon=True,
    )
    thread.start()


def _run_experiment(store: ExperimentStore, experiment_id: str, capability_id: str) -> None:
    demo_number = CAPABILITY_TO_DEMO[capability_id]
    try:
        settings = load_settings()
        client = create_client(settings)
    except Exception as exc:  # noqa: BLE001 - converted to a safe event below
        _emit_setup_error(store, experiment_id, "plain", exc)
        _emit_setup_error(store, experiment_id, "harness", exc)
        return

    _run_side(store, experiment_id, demo_number, False, settings, client)
    _run_side(store, experiment_id, demo_number, True, settings, client)


def _run_side(
    store: ExperimentStore,
    experiment_id: str,
    demo_number: int,
    harness: bool,
    settings: Settings,
    client: object,
) -> None:
    side: RunSide = "harness" if harness else "plain"
    store.set_run(experiment_id, side, RunSnapshot(status="running"))
    reporter = StoreReporter(store, experiment_id, side)
    try:
        workspace = prepare_workspace(demo_number, harness)
        exit_code = _DEMO_RUNNERS[demo_number](
            client,
            settings,
            workspace,
            harness,
            reporter,
        )
        outcome = _outcome(demo_number, harness, exit_code, reporter)
        terminal = reporter.pending_result or DemoEvent(
            stage="result",
            status=outcome,
            title="运行完成",
            summary=_result_summary(outcome),
            evidence={"calls": reporter.calls},
        )
        store.finish_run(
            experiment_id,
            side,
            reporter.snapshot("completed", outcome),
            "result",
            terminal.status,
            sanitize_text(terminal.title),
            sanitize_text(terminal.summary),
            build_evidence("result", terminal.evidence),
        )
    except Exception as exc:  # noqa: BLE001 - keep a background failure inside the API
        store.finish_run(
            experiment_id,
            side,
            reporter.snapshot("failed", "infrastructure_error"),
            "error",
            "infrastructure_error",
            "运行基础设施错误",
            "运行未能启动或完成。",
            {"error": f"{type(exc).__name__}: 运行未能启动或完成。"},
        )


def _emit_setup_error(
    store: ExperimentStore,
    experiment_id: str,
    side: RunSide,
    exc: Exception,
) -> None:
    store.finish_run(
        experiment_id,
        side,
        RunSnapshot(status="failed", outcome="infrastructure_error"),
        "error",
        "infrastructure_error",
        "配置错误",
        "服务端配置不可用。",
        {"error": f"{type(exc).__name__}: 服务端配置不可用。"},
    )


def _event_stage(value: str) -> EventStage:
    allowed = {
        "input",
        "llm",
        "tool",
        "write",
        "test",
        "feedback",
        "approval",
        "handoff",
        "grounding",
        "result",
        "error",
    }
    if value not in allowed:
        raise ValueError(f"未知事件阶段: {value}")
    return cast(EventStage, value)


def _outcome(demo_number: int, harness: bool, exit_code: int, reporter: StoreReporter) -> str:
    if demo_number == 1:
        return "analysis"
    if demo_number == 2 and not harness:
        return "proposal"
    if demo_number == 4 and harness and reporter.capability_outcome == "controlled_stop":
        return "controlled_stop"
    if demo_number == 5 and reporter.capability_outcome == "handoff_error":
        return "handoff_error"
    if demo_number == 6 and harness and reporter.capability_outcome == "grounding_error":
        return "grounding_error"
    return "passed" if exit_code == 0 else "failed"


def _result_summary(outcome: str) -> str:
    return {
        "analysis": "分析完成；工作区按预期未修改。",
        "proposal": "仅生成提案；未声明完成仓库修改。",
        "passed": "确定性评价通过。",
        "failed": "确定性评价未通过。",
        "controlled_stop": "控制门禁已生效，任务未执行。",
        "handoff_error": "交接记录不可用，无法继续本次实验。",
        "grounding_error": "未取得当前政策依据。",
    }[outcome]


def _sanitize(value: str) -> str:
    """Compatibility alias for callers of the previous runner helper."""
    return sanitize_text(value)
