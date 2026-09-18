"""Short-lived, thread-safe experiment state and event storage."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from threading import Condition, RLock
from uuid import uuid4

from harness_demo.web.models import (
    EventEvidence,
    EventStage,
    ExperimentEvent,
    ExperimentResult,
    RunSide,
    RunSnapshot,
)
from harness_demo.web.presentation import build_comparison, build_evidence

RETENTION = timedelta(minutes=30)


class ExperimentNotFound(KeyError):
    """Raised when an experiment has expired or does not exist."""


class ApprovalNotFound(KeyError):
    """Raised when an approval cannot be found in the short-lived store."""


class ApprovalAlreadyDecided(ValueError):
    """Raised when an approval decision was already recorded."""


class ExperimentStore:
    def __init__(self) -> None:
        self._records: dict[str, _Record] = {}
        self._lock = RLock()
        self._changed = Condition(self._lock)

    def create(self, capability_id: str) -> str:
        with self._changed:
            self._cleanup_locked()
            experiment_id = f"exp_{uuid4().hex[:12]}"
            self._records[experiment_id] = _Record(capability_id=capability_id)
            return experiment_id

    def emit(
        self,
        experiment_id: str,
        side: RunSide,
        stage: EventStage,
        status: str,
        title: str,
        summary: str,
        evidence: dict[str, object] | EventEvidence | None = None,
    ) -> ExperimentEvent:
        with self._changed:
            record = self._get_locked(experiment_id)
            event = self._append_event_locked(
                record, experiment_id, side, stage, status, title, summary, evidence
            )
            self._changed.notify_all()
            return event

    def finish_run(
        self,
        experiment_id: str,
        side: RunSide,
        snapshot: RunSnapshot,
        stage: EventStage,
        event_status: str,
        title: str,
        summary: str,
        evidence: dict[str, object] | EventEvidence | None = None,
    ) -> ExperimentEvent:
        """Atomically publish the final event and terminal run snapshot."""
        with self._changed:
            record = self._get_locked(experiment_id)
            if side == "plain":
                record.plain = snapshot
            else:
                record.harness = snapshot
                record.completed_at = datetime.now(UTC)
            event = self._append_event_locked(
                record,
                experiment_id,
                side,
                stage,
                event_status,
                title,
                summary,
                evidence,
            )
            self._changed.notify_all()
            return event

    def set_run(self, experiment_id: str, side: RunSide, snapshot: RunSnapshot) -> None:
        with self._changed:
            record = self._get_locked(experiment_id)
            if side == "plain":
                record.plain = snapshot
            else:
                record.harness = snapshot
            if side == "harness" and snapshot.status in {"completed", "failed"}:
                record.completed_at = datetime.now(UTC)
            self._changed.notify_all()

    def open_approval(self, experiment_id: str, side: RunSide, action: str, scope: str) -> str:
        with self._changed:
            record = self._get_locked(experiment_id)
            approval_id = f"apr_{uuid4().hex[:12]}"
            record.approvals[approval_id] = _Approval(side=side, action=action, scope=scope)
            return approval_id

    def decide_approval(self, approval_id: str, approved: bool) -> None:
        with self._changed:
            self._cleanup_locked()
            approval = self._find_approval_locked(approval_id)
            if approval.decision is not None:
                raise ApprovalAlreadyDecided(approval_id)
            approval.decision = "approved" if approved else "rejected"
            self._changed.notify_all()

    def wait_for_approval(self, approval_id: str, timeout_seconds: int) -> str:
        with self._changed:
            approval = self._find_approval_locked(approval_id)
            if approval.decision is None:
                self._changed.wait_for(
                    lambda: approval.decision is not None, timeout=timeout_seconds
                )
            if approval.decision is None:
                approval.decision = "timed_out"
            return approval.decision

    def result(self, experiment_id: str) -> ExperimentResult:
        with self._lock:
            record = self._get_locked(experiment_id)
            status = "starting"
            if record.plain.status == "failed" or record.harness.status == "failed":
                status = "incomplete"
            elif record.harness.status == "completed":
                status = "completed"
            elif record.plain.status == "running" or record.harness.status == "running":
                status = "running"
            return ExperimentResult(
                experimentId=experiment_id,
                capabilityId=record.capability_id,
                status=status,
                plain=record.plain,
                harness=record.harness,
                events=list(record.events),
                comparison=build_comparison(record.capability_id, record.plain, record.harness),
            )

    def events_after(self, experiment_id: str, event_id: str | None) -> list[ExperimentEvent]:
        with self._lock:
            record = self._get_locked(experiment_id)
            if not event_id:
                return list(record.events)
            for index, event in enumerate(record.events):
                if event.id == event_id:
                    return list(record.events[index + 1 :])
            return list(record.events)

    def stream(self, experiment_id: str, event_id: str | None) -> Iterator[ExperimentEvent]:
        last_id = event_id
        while True:
            with self._changed:
                events = self.events_after(experiment_id, last_id)
                if not events:
                    record = self._get_locked(experiment_id)
                    if record.harness.status in {"completed", "failed"}:
                        return
                    self._changed.wait(timeout=15)
                    continue
            for event in events:
                last_id = event.id
                yield event

    def _get_locked(self, experiment_id: str) -> _Record:
        self._cleanup_locked()
        try:
            return self._records[experiment_id]
        except KeyError as exc:
            raise ExperimentNotFound(experiment_id) from exc

    def _find_approval_locked(self, approval_id: str) -> _Approval:
        for record in self._records.values():
            approval = record.approvals.get(approval_id)
            if approval is not None:
                return approval
        raise ApprovalNotFound(approval_id)

    def _append_event_locked(
        self,
        record: _Record,
        experiment_id: str,
        side: RunSide,
        stage: EventStage,
        status: str,
        title: str,
        summary: str,
        evidence: dict[str, object] | EventEvidence | None,
    ) -> ExperimentEvent:
        record.sequence += 1
        event = ExperimentEvent(
            id=f"evt_{record.sequence}_{uuid4().hex[:6]}",
            experimentId=experiment_id,
            side=side,
            stage=stage,
            status=status,
            sequence=record.sequence,
            occurredAt=datetime.now(UTC),
            title=title,
            summary=summary,
            evidence=(
                evidence if isinstance(evidence, EventEvidence) else build_evidence(stage, evidence)
            ),
        )
        record.events.append(event)
        return event

    def _cleanup_locked(self) -> None:
        now = datetime.now(UTC)
        expired = [
            key
            for key, record in self._records.items()
            if record.completed_at is not None and now - record.completed_at > RETENTION
        ]
        for key in expired:
            del self._records[key]


class _Record:
    def __init__(self, capability_id: str) -> None:
        self.capability_id = capability_id
        self.events: list[ExperimentEvent] = []
        self.sequence = 0
        self.plain = RunSnapshot(status="waiting")
        self.harness = RunSnapshot(status="waiting")
        self.completed_at: datetime | None = None
        self.approvals: dict[str, _Approval] = {}


class _Approval:
    def __init__(self, side: RunSide, action: str, scope: str) -> None:
        self.side = side
        self.action = action
        self.scope = scope
        self.decision: str | None = None
