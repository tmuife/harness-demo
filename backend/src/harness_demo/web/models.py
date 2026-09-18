"""Public, bounded models used by the Harness Lab API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CapabilityStatus = Literal["available", "planned"]
RunSide = Literal["plain", "harness"]
RunStatus = Literal["waiting", "running", "completed", "failed"]
EventStage = Literal[
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
]
FinalTestStatus = Literal["passed", "failed", "not_run", "unknown"]
Outcome = Literal[
    "passed",
    "failed",
    "analysis",
    "proposal",
    "controlled_stop",
    "handoff_error",
    "grounding_error",
    "infrastructure_error",
]


class HarnessComponent(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    title: str


class DemoTask(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    number: int
    question: str
    plain_condition: str = Field(alias="plainCondition")
    harness_condition: str = Field(alias="harnessCondition")
    completion_definition: list[str] = Field(alias="completionDefinition")
    expected_evidence: list[str] = Field(alias="expectedEvidence")
    talk_track: str = Field(alias="talkTrack")


class Capability(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    id: str
    title: str
    description: str
    evidence: str
    status: CapabilityStatus
    demo_task: DemoTask | None = Field(default=None, alias="demoTask")
    primary_components: list[HarnessComponent] = Field(
        default_factory=list, alias="primaryComponents"
    )
    supporting_components: list[HarnessComponent] = Field(
        default_factory=list, alias="supportingComponents"
    )
    coverage_note: str | None = Field(default=None, alias="coverageNote")


class TaskBrief(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    summary: str


class CreateExperimentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(alias="taskId")
    capabilities: list[str] = Field(min_length=1, max_length=1)


class ApprovalDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approved: bool


class RunSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    status: RunStatus
    outcome: Outcome | None = None
    calls: int = 0
    input_sources: list[str] = Field(default_factory=list, alias="inputSources")
    modified_files: list[str] = Field(default_factory=list, alias="modifiedFiles")
    test_runs: int = Field(default=0, alias="testRuns")
    feedback_rounds: int = Field(default=0, alias="feedbackRounds")
    final_test: FinalTestStatus = Field(default="unknown", alias="finalTest")
    checks: dict[str, bool] = Field(default_factory=dict)
    workspace_unchanged: bool | None = Field(default=None, alias="workspaceUnchanged")
    scope_ok: bool | None = Field(default=None, alias="scopeOk")
    proposal_only: bool = Field(default=False, alias="proposalOnly")
    max_turns: int | None = Field(default=None, alias="maxTurns")
    stop_reason: str | None = Field(default=None, alias="stopReason")
    approval_status: str | None = Field(default=None, alias="approvalStatus")
    protected_action_executed: bool | None = Field(default=None, alias="protectedActionExecuted")
    handoff_available: bool | None = Field(default=None, alias="handoffAvailable")
    handoff_valid: bool | None = Field(default=None, alias="handoffValid")
    policy_version: str | None = Field(default=None, alias="policyVersion")
    effective_date: str | None = Field(default=None, alias="effectiveDate")
    grounding_used: bool | None = Field(default=None, alias="groundingUsed")
    task_outcome: str | None = Field(default=None, alias="taskOutcome")
    capability_outcome: str | None = Field(default=None, alias="capabilityOutcome")
    rejected_requests: int = Field(default=0, alias="rejectedRequests")


class EventEvidence(BaseModel):
    """Bounded stage-specific fields accepted by the public event contract."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    kind: EventStage
    sources: list[str] = Field(default_factory=list)
    context_count: int | None = Field(default=None, alias="contextCount")
    turn: int | None = None
    target_turn: int | None = Field(default=None, alias="targetTurn")
    call: bool = False
    output: str | None = None
    tool_name: str | None = Field(default=None, alias="toolName")
    path: str | None = None
    characters: int | None = None
    ok: bool | None = None
    command: str | None = None
    return_code: int | None = Field(default=None, alias="returnCode")
    passed: bool | None = None
    passed_count: int | None = Field(default=None, alias="passedCount")
    failed_count: int | None = Field(default=None, alias="failedCount")
    failed_tests: list[str] = Field(default_factory=list, alias="failedTests")
    diff: str | None = None
    modified_files: list[str] = Field(default_factory=list, alias="modifiedFiles")
    calls: int | None = None
    test_runs: int | None = Field(default=None, alias="testRuns")
    feedback_rounds: int | None = Field(default=None, alias="feedbackRounds")
    final_test: FinalTestStatus | None = Field(default=None, alias="finalTest")
    checks: dict[str, bool] = Field(default_factory=dict)
    workspace_unchanged: bool | None = Field(default=None, alias="workspaceUnchanged")
    scope_ok: bool | None = Field(default=None, alias="scopeOk")
    proposal_only: bool | None = Field(default=None, alias="proposalOnly")
    error: str | None = None
    approval_id: str | None = Field(default=None, alias="approvalId")
    action: str | None = None
    scope: str | None = None
    input_priority: list[str] = Field(default_factory=list, alias="inputPriority")
    schema_valid: bool | None = Field(default=None, alias="schemaValid")
    permission_granted: bool | None = Field(default=None, alias="permissionGranted")
    executed: bool | None = None
    max_turns: int | None = Field(default=None, alias="maxTurns")
    stop_reason: str | None = Field(default=None, alias="stopReason")
    approval_status: str | None = Field(default=None, alias="approvalStatus")
    protected_action_executed: bool | None = Field(default=None, alias="protectedActionExecuted")
    session: str | None = None
    handoff_available: bool | None = Field(default=None, alias="handoffAvailable")
    handoff_valid: bool | None = Field(default=None, alias="handoffValid")
    handoff_fields: list[str] = Field(default_factory=list, alias="handoffFields")
    source_label: str | None = Field(default=None, alias="sourceLabel")
    policy_version: str | None = Field(default=None, alias="policyVersion")
    effective_date: str | None = Field(default=None, alias="effectiveDate")
    grounding_used: bool | None = Field(default=None, alias="groundingUsed")
    task_outcome: str | None = Field(default=None, alias="taskOutcome")
    capability_outcome: str | None = Field(default=None, alias="capabilityOutcome")
    rejected_requests: int | None = Field(default=None, alias="rejectedRequests")


class ExperimentEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    experiment_id: str = Field(alias="experimentId")
    side: RunSide
    stage: EventStage
    status: str
    sequence: int
    occurred_at: datetime = Field(alias="occurredAt")
    title: str
    summary: str
    evidence: EventEvidence


class ComparisonMetric(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    plain: str
    harness: str


class ComparisonSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    observation: str
    qualification: str
    metrics: list[ComparisonMetric]


class ExperimentCreated(BaseModel):
    model_config = ConfigDict(frozen=True)

    experiment_id: str = Field(alias="experimentId")
    capability_id: str = Field(alias="capabilityId")
    plain_run_id: str = Field(alias="plainRunId")
    harness_run_id: str = Field(alias="harnessRunId")


class ExperimentResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    experiment_id: str = Field(alias="experimentId")
    capability_id: str = Field(alias="capabilityId")
    status: Literal["starting", "running", "completed", "incomplete"]
    plain: RunSnapshot
    harness: RunSnapshot
    events: list[ExperimentEvent]
    comparison: ComparisonSummary | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    detail: str
