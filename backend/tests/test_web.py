from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from harness_demo.llm import Settings
from harness_demo.reporting import DemoEvent
from harness_demo.web import app as app_module
from harness_demo.web import runner
from harness_demo.web.app import _sse
from harness_demo.web.models import RunSnapshot
from harness_demo.web.runner import _run_experiment, _sanitize
from harness_demo.web.store import ExperimentNotFound, ExperimentStore


def test_catalog_endpoints_expose_public_metadata() -> None:
    client = TestClient(app_module.app)

    capabilities = client.get("/api/capabilities")
    task = client.get("/api/task")

    assert capabilities.status_code == 200
    assert [item["id"] for item in capabilities.json()] == [
        "understand",
        "act",
        "prove",
        "control",
        "continue",
        "ground",
    ]
    assert task.json()["id"] == "shipping-policy-upgrade"
    payload = capabilities.json()
    assert all(item["status"] == "available" for item in payload)
    assert payload[3]["demoTask"]["number"] == 4
    assert payload[4]["primaryComponents"][0]["id"] == "memory"
    assert "子 Agent" in payload[5]["coverageNote"]


def test_unknown_experiment_request_does_not_start_runner(monkeypatch) -> None:
    started: list[tuple[str, str]] = []
    monkeypatch.setattr(
        app_module,
        "start_experiment",
        lambda store, experiment_id, capability_id: started.append((experiment_id, capability_id)),
    )
    client = TestClient(app_module.app)

    response = client.post(
        "/api/experiments",
        json={"taskId": "shipping-policy-upgrade", "capabilities": ["unknown"]},
    )

    assert response.status_code == 400
    assert started == []


def test_available_control_experiment_starts_runner(monkeypatch) -> None:
    started: list[str] = []
    monkeypatch.setattr(
        app_module,
        "start_experiment",
        lambda _store, _experiment_id, capability_id: started.append(capability_id),
    )

    response = TestClient(app_module.app).post(
        "/api/experiments",
        json={"taskId": "shipping-policy-upgrade", "capabilities": ["control"]},
    )

    assert response.status_code == 201
    assert started == ["control"]


def test_approval_decision_is_exactly_once(monkeypatch) -> None:
    store = ExperimentStore()
    experiment_id = store.create("control")
    approval_id = store.open_approval(
        experiment_id, "harness", "写入 src/shipping.py", "src/shipping.py"
    )
    monkeypatch.setattr(app_module, "store", store)
    client = TestClient(app_module.app)

    accepted = client.post(f"/api/approvals/{approval_id}", json={"approved": True})
    repeated = client.post(f"/api/approvals/{approval_id}", json={"approved": False})

    assert accepted.status_code == 204
    assert repeated.status_code == 409
    assert store.wait_for_approval(approval_id, 1) == "approved"


def test_store_orders_and_replays_events() -> None:
    store = ExperimentStore()
    experiment_id = store.create("understand")
    first = store.emit(experiment_id, "plain", "input", "running", "输入", "工单")
    second = store.emit(experiment_id, "plain", "llm", "info", "调用", "分析")

    assert [event.sequence for event in store.events_after(experiment_id, None)] == [1, 2]
    assert store.events_after(experiment_id, first.id) == [second]
    assert store.events_after(experiment_id, "unknown") == [first, second]
    assert "event: experiment" in _sse(second)
    assert second.id in _sse(second)


def test_event_endpoint_replays_then_closes(monkeypatch) -> None:
    store = ExperimentStore()
    experiment_id = store.create("understand")
    event = store.emit(experiment_id, "plain", "input", "running", "输入", "工单")
    store.set_run(experiment_id, "harness", RunSnapshot(status="completed", outcome="analysis"))
    monkeypatch.setattr(app_module, "store", store)

    response = TestClient(app_module.app).get(f"/api/experiments/{experiment_id}/events")

    assert response.status_code == 200
    assert f"id: {event.id}" in response.text
    assert '"sequence": 1' in response.text


def test_store_expires_only_completed_experiments() -> None:
    store = ExperimentStore()
    completed_id = store.create("understand")
    active_id = store.create("act")
    store.set_run(completed_id, "harness", RunSnapshot(status="completed", outcome="analysis"))
    store._records[completed_id].completed_at = datetime.now(UTC) - timedelta(minutes=31)
    store._cleanup_locked()

    try:
        store.result(completed_id)
    except ExperimentNotFound:
        pass
    else:
        raise AssertionError("expired experiment must not be returned")
    assert store.result(active_id).status == "starting"


def test_result_is_running_when_harness_starts_after_plain() -> None:
    store = ExperimentStore()
    experiment_id = store.create("understand")
    store.set_run(experiment_id, "plain", RunSnapshot(status="completed", outcome="analysis"))
    store.set_run(experiment_id, "harness", RunSnapshot(status="running"))

    assert store.result(experiment_id).status == "running"


def test_orchestrator_runs_plain_before_harness(monkeypatch, tmp_path) -> None:
    store = ExperimentStore()
    experiment_id = store.create("understand")
    calls: list[bool] = []
    settings = Settings("key", "https://example.invalid", "test-model")

    def fake_run(client, settings, workspace, harness, reporter):
        calls.append(harness)
        reporter.emit(
            DemoEvent(
                "input",
                "ready",
                "模型获得项目输入",
                "工单",
                {"sources": ["DEMO_TICKET.md"], "context_count": 1},
            )
        )
        reporter.emit(
            DemoEvent(
                "result",
                "analysis",
                "分析完成",
                "工作区未修改",
                {
                    "calls": 1,
                    "final_test": "not_run",
                    "workspace_unchanged": True,
                },
            )
        )
        return 0

    monkeypatch.setattr("harness_demo.web.runner.load_settings", lambda: settings)
    monkeypatch.setattr("harness_demo.web.runner.create_client", lambda active_settings: object())
    monkeypatch.setattr(
        "harness_demo.web.runner.prepare_workspace", lambda number, harness: tmp_path
    )
    monkeypatch.setitem(runner._DEMO_RUNNERS, 1, fake_run)

    _run_experiment(store, experiment_id, "understand")

    result = store.result(experiment_id)
    assert calls == [False, True]
    assert result.plain.status == "completed"
    assert result.harness.status == "completed"
    assert [event.side for event in result.events if event.stage == "input"] == [
        "plain",
        "harness",
    ]
    assert result.comparison is not None
    assert "本次运行" in result.comparison.observation


def test_sanitize_hides_backend_absolute_path() -> None:
    assert "<backend>" in _sanitize(
        "/home/ubuntu/project/doc/hermes-agent/UpSkill/demostration/backend/x"
    )
    assert "secret" not in _sanitize("OPENAI_API_KEY=secret")
    assert "secret" not in _sanitize("Authorization: Bearer secret")
