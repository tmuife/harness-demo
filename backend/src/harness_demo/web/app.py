"""FastAPI application exposing Harness Lab experiments."""

from __future__ import annotations

import json
from collections.abc import Iterator

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Response, status
from fastapi.responses import StreamingResponse

from harness_demo.web.catalog import CAPABILITIES, TASK, find_capability
from harness_demo.web.models import (
    ApprovalDecisionRequest,
    Capability,
    CreateExperimentRequest,
    ErrorResponse,
    ExperimentCreated,
    ExperimentEvent,
    ExperimentResult,
    TaskBrief,
)
from harness_demo.web.runner import start_experiment
from harness_demo.web.store import (
    ApprovalAlreadyDecided,
    ApprovalNotFound,
    ExperimentNotFound,
    ExperimentStore,
)

app = FastAPI(title="Harness Lab API", version="0.1.0")
store = ExperimentStore()


@app.get("/api/capabilities", response_model=list[Capability])
def list_capabilities() -> tuple[Capability, ...]:
    return CAPABILITIES


@app.get("/api/task", response_model=TaskBrief)
def get_task() -> TaskBrief:
    return TASK


@app.post(
    "/api/experiments",
    response_model=ExperimentCreated,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_experiment(request: CreateExperimentRequest) -> ExperimentCreated:
    if request.task_id != TASK.id:
        raise HTTPException(status_code=400, detail="未知任务。")
    capability = find_capability(request.capabilities[0])
    if capability is None:
        raise HTTPException(status_code=400, detail="未知 Harness 能力。")
    if capability.status != "available":
        raise HTTPException(status_code=400, detail="该 Harness 能力尚未开放运行。")

    experiment_id = store.create(capability.id)
    start_experiment(store, experiment_id, capability.id)
    return ExperimentCreated(
        experimentId=experiment_id,
        capabilityId=capability.id,
        plainRunId=f"{experiment_id}:plain",
        harnessRunId=f"{experiment_id}:harness",
    )


@app.get(
    "/api/experiments/{experiment_id}/result",
    response_model=ExperimentResult,
    responses={404: {"model": ErrorResponse}},
)
def get_result(experiment_id: str) -> ExperimentResult:
    try:
        return store.result(experiment_id)
    except ExperimentNotFound:
        raise HTTPException(status_code=404, detail="实验不存在或已过期。") from None


@app.post("/api/approvals/{approval_id}", status_code=status.HTTP_204_NO_CONTENT)
def decide_approval(approval_id: str, request: ApprovalDecisionRequest) -> Response:
    try:
        store.decide_approval(approval_id, request.approved)
    except ApprovalNotFound:
        raise HTTPException(status_code=404, detail="审批不存在或已过期。") from None
    except ApprovalAlreadyDecided:
        raise HTTPException(status_code=409, detail="审批已处理。") from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/experiments/{experiment_id}/events", responses={404: {"model": ErrorResponse}})
def stream_events(
    experiment_id: str,
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
) -> Response:
    try:
        store.result(experiment_id)
    except ExperimentNotFound:
        raise HTTPException(status_code=404, detail="实验不存在或已过期。") from None

    def generate() -> Iterator[str]:
        try:
            for event in store.stream(experiment_id, last_event_id):
                yield _sse(event)
        except ExperimentNotFound:
            return

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _sse(event: ExperimentEvent) -> str:
    payload = json.dumps(event.model_dump(by_alias=True, mode="json"), ensure_ascii=False)
    return f"id: {event.id}\nevent: experiment\ndata: {payload}\n\n"


def main() -> None:
    uvicorn.run("harness_demo.web.app:app", host="127.0.0.1", port=8000, reload=False)
