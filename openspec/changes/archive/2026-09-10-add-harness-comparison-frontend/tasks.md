## 1. Backend API foundation

- [x] 1.1 Add the minimal FastAPI and ASGI server dependencies to `backend/pyproject.toml`, refresh `uv.lock`, and expose a documented development command without changing the existing `harness-demo` CLI entry point.
- [x] 1.2 Create typed API schemas for capability metadata, task metadata, experiment creation, run state, event stages, evidence payloads, final results, and bounded error responses.
- [x] 1.3 Implement server-owned task and capability catalogs with all six capabilities, marking only `understand`, `act`, and `prove` available, and reject unknown, planned, empty, or multi-capability first-phase requests before workspace creation.
- [x] 1.4 Add thin endpoints for `GET /api/capabilities` and `GET /api/task`, returning explicit response schemas and no sensitive backend configuration.

## 2. Experiment events, storage, and orchestration

- [x] 2.1 Introduce a small typed event sink/collector that assigns stable IDs and monotonic sequence numbers, plus a console sink that preserves existing CLI labels and readable output.
- [x] 2.2 Refactor shared and Demo 1–3 reporting boundaries to emit structured events while preserving current CLI behavior, workspace restrictions, output truncation, and deterministic testability.
- [x] 2.3 Implement an in-memory experiment store for state, events, and results, with thread-safe access, 30-minute expiry for completed experiments, cleanup that never removes active runs, and explicit not-found handling.
- [x] 2.4 Implement an experiment orchestrator that creates isolated PLAIN/HARNESS workspaces, runs PLAIN to a terminal state before starting HARNESS, records waiting/running/terminal states, and distinguishes infrastructure errors from evaluated model results.
- [x] 2.5 Add `POST /api/experiments` and `GET /api/experiments/{experiment_id}/result` using the validated server catalogs and bounded response models.
- [x] 2.6 Add `GET /api/experiments/{experiment_id}/events` as an SSE stream with event IDs, replay after `Last-Event-ID`, ordered delivery, terminal closure, disconnect handling, and no unbounded polling or buffering.

## 3. Demo adapters and result evidence

- [x] 3.1 Adapt Demo 1 to emit input, LLM, analysis-check, and result evidence while treating an unchanged workspace as the expected analysis outcome.
- [x] 3.2 Adapt Demo 2 to emit tool, write, test, diff, proposal-only, scope-check, and final result evidence without weakening tool or path validation.
- [x] 3.3 Adapt Demo 3 to emit each generation, write, test, feedback, call-count, diff, and terminal result event while keeping test source hidden from the model.
- [x] 3.4 Centralize API-facing evidence sanitization so SDK failures, authentication data, host absolute paths, unrestricted command input, and oversized model/test output cannot reach responses or SSE events.

## 4. Backend verification

- [x] 4.1 Add API tests for capability/task responses and experiment validation, including proof that rejected requests do not create workspaces or call an LLM.
- [x] 4.2 Add deterministic orchestration tests proving PLAIN completes before HARNESS starts, each side uses a clean workspace, and infrastructure errors are not reported as evaluated FAIL results.
- [x] 4.3 Add store and SSE tests for ordering, deduplication identifiers, replay after `Last-Event-ID`, terminal closure, active-run retention, 30-minute expiry, and missing experiments.
- [x] 4.4 Add Demo 1–3 event adapter and sanitization tests, then run all existing backend pytest and Ruff checks to confirm CLI compatibility and security boundaries.

## 5. Frontend experiment state and API client

- [x] 5.1 Replace the Vite starter content with a feature-local `experiment` structure containing strict TypeScript domain types, API helpers, components, reducer, and styles without adding a production UI or global-state library.
- [x] 5.2 Implement typed clients for capability/task loading, experiment creation, result retrieval, SSE subscription with last-event tracking, and the future controlled approval action; render all server content as text.
- [x] 5.3 Implement a reducer for loading, selection, starting, PLAIN running, HARNESS waiting/running, reconnecting, completed, incomplete, and recovery-failed states, with event ID deduplication and sequence ordering.
- [x] 5.4 Store the latest experiment ID in `sessionStorage`, restore retained state and results on page load, resume SSE for active runs, and clear missing or expired IDs with a non-failure notice.

## 6. Harness Lab interface

- [x] 6.1 Build the responsive experiment-console shell and task brief using the graphite, warm-white, lime, orange, and red visual language, with deliberate typography, visible focus styles, and reduced-motion support.
- [x] 6.2 Build the six-item capability panel with descriptions, evidence labels, available/planned states, single-selection replacement behavior, explanatory planned details, and correct disabled/run-lock behavior.
- [x] 6.3 Build PLAIN and HARNESS comparison lanes that remain side by side on desktop, use accessible tabs on small screens, and visibly show the HARNESS waiting state until PLAIN terminates.
- [x] 6.4 Build the event timeline and evidence drawer for all controlled event stages, using expandable summaries, safe text rendering, bounded scrolling, copy actions, and layouts resilient to long content.
- [x] 6.5 Build result summaries that compare calls, changed files, tests, constraints, PASS/FAIL, analysis-only, proposal-only, incomplete, and infrastructure-error outcomes without relying on color alone.
- [x] 6.6 Build the reusable inline approval card for future Control events, showing action and scope, submitting one approve/reject decision, disabling duplicate actions, and retaining the confirmed decision in timeline context.
- [x] 6.7 Complete loading, no-selection, planned, startup-error, reconnecting, expired-recovery, empty-evidence, and long-output states with concise recovery actions.

## 7. Frontend and integration verification

- [x] 7.1 Add a lightweight Vitest and Testing Library setup, then test capability selection/replacement, planned capability behavior, run locking, reducer event ordering/deduplication, and session recovery.
- [x] 7.2 Test desktop/mobile lane behavior, keyboard access, accessible labels and status announcements, inline approval state, safe evidence rendering, infrastructure errors, and reduced-motion behavior.
- [x] 7.3 Configure the frontend development API target without placing secrets in `VITE_` variables, and document separate frontend/backend development commands and the same-origin production `/api` expectation.
- [x] 7.4 Run frontend lint, tests, and production build; run backend pytest and Ruff; then manually exercise Understand, Act, and Prove through the Web UI against a configured backend and record any real-LLM variability separately from deterministic checks.
