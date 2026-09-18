## 1. Confirm design and establish shared contracts

- [ ] 1.1 Complete the remaining verification in `improve-comparison-readability`, sync or archive its delta spec, and confirm the resulting reporter and frontend phase model as this change's baseline.
- [x] 1.2 Resolve the decisions in `design.md` Open Questions for approval timeout/outcome, handoff transport, task prompt visibility, component coverage, Ground provider, live-demo selection, and sub-Agent scope; update artifacts before implementation where a decision changes behavior.
- [x] 1.3 Add typed backend models for the 11 stable component IDs, per-Demo task detail, primary/supporting coverage, and explicit uncovered-component notes without exposing internal prompts or configuration.
- [x] 1.4 Extend public event evidence and run snapshots with only the fields required for prompt assembly, tool validation, loop termination, approval, handoff, grounding, task outcome, and capability outcome; mirror them in strict frontend types.
- [x] 1.5 Extend the shipping fixture with a clearly stale cached policy, a schema-valid versioned current provider policy, and any Demo-specific synthetic files while preserving the immutable source fixture and test-file boundary.
- [x] 1.6 Add model and catalogue tests for complete six-Demo task metadata, valid component references, duplicate component relationships, uncovered sub-Agent orchestration, bounded text, and absence of secrets or absolute paths.

## 2. Make the existing Demo 1–3 mechanisms explicit

- [x] 2.1 Extend Understand input reporting with public source categories and prompt assembly priority facts while preserving its read-only analysis behavior and hiding system prompts.
- [x] 2.2 Extend Act tool reporting to distinguish structured tool call receipt, schema validation, permission decision, actual execution, and result feedback without claiming unexecuted steps.
- [x] 2.3 Extend Prove reporting with failure classification, configured and actual turns, and deterministic stop reason while continuing to hide test source from the model.
- [x] 2.4 Update Understand, Act, and Prove comparison builders and focused tests for the new component evidence without changing their current PLAIN/HARNESS inputs or expected outcome semantics.

## 3. Implement Demo 4 Control

- [x] 3.1 Implement `demo_4_control.py` with real Responses tool calls, a wider but workspace-bounded PLAIN write policy, a `src/shipping.py` HARNESS write allowlist, fixed tests, bounded output, and semantic reporter events.
- [x] 3.2 Add a one-time CLI approval gate before the first valid HARNESS write, including explicit approve, reject, EOF, invalid-input, and configured-timeout behavior.
- [x] 3.3 Add a thread-safe in-memory Web approval coordinator with stable approval IDs, bounded waiting, replayable pending state, exactly-once decisions, conflict responses, and cleanup on terminal or expired experiments.
- [x] 3.4 Ensure invalid paths, test-file writes, unknown tools, invalid arguments, and non-fixed commands are rejected before execution on both sides and returned to the model as bounded tool errors.
- [x] 3.5 Add deterministic Control evaluation and comparison output that separately reports allowed scope, approval decision, protected action execution, rejected requests, modified files, tests, task completion, and control-gate outcome.
- [x] 3.6 Add fake-client and Web tests for no-approval PLAIN execution, HARNESS approve/reject/timeout, no model boundary violation, optional actual violation, duplicate decisions, refresh/SSE recovery, and infrastructure failure.

## 4. Implement Demo 5 Continue

- [x] 4.1 Implement `demo_5_continue.py` with separate Session A and Session B Responses inputs and prove in tests that no response/session history is shared between them.
- [x] 4.2 Keep Session A read-only and implement the confirmed schema or `save_handoff` tool for bounded completed-work, findings, remaining-work, target-file, and verification-command fields.
- [x] 4.3 Persist a valid HARNESS handoff only inside the current disposable workspace and inject it into Session B with an explicit source boundary; ensure PLAIN Session B receives no Session A content.
- [x] 4.4 Implement invalid, missing, oversized, and unsafe handoff handling without heuristic free-text field recovery, including the confirmed finite recovery or terminal behavior.
- [x] 4.5 Let Session B perform the allowed implementation and fixed validation, then emit deterministic session-boundary, handoff, modification, test, repetition, and completion evidence.
- [x] 4.6 Add fake-client tests for session isolation, read-only Session A, PLAIN information absence, valid HARNESS continuation, malformed handoff, workspace cleanup, maximum calls, and final evaluation.

## 5. Implement Demo 6 Ground

- [x] 5.1 Implement `demo_6_ground.py` so PLAIN receives only the ticket and explicitly stale cache while HARNESS can call a read-only `get_current_shipping_policy` tool backed by the local provider fixture.
- [x] 5.2 Validate provider JSON against an explicit whitelist schema and preserve the data/instruction boundary by rejecting unknown, oversized, malformed, or instruction-like fields from prompt assembly.
- [x] 5.3 Record grounding source, tool use, policy version, effective date, allowed policy values, file changes, and contract-test evidence without representing the local provider as a live network service.
- [x] 5.4 Build deterministic Ground evaluation that requires successful current-policy retrieval and contract verification before using the “基于当前依据完成” result label, with no fallback to model claims.
- [x] 5.5 Add fake-client tests for stale-only PLAIN input, successful current-policy tool use, no tool call, malformed/missing provider data, injection-like fields, wrong version/date, scope violations, and final contract outcomes.

## 6. Integrate all six demos into CLI and Web backend

- [x] 6.1 Extend `VALID_DEMOS`, CLI parser/list/dispatch, workspace naming, capability-to-demo mapping, and runner dispatch from Demo 1–3 to Demo 1–6 while retaining no-configuration behavior for `list` and invalid input.
- [x] 6.2 Populate the server-owned catalogue with six task details and the reviewed primary/supporting component mapping, then mark Control, Continue, and Ground available only after their complete paths pass tests.
- [x] 6.3 Extend Web evidence construction, sanitization, result snapshots, and deterministic comparison builders for approval, handoff, grounding, stop reasons, task outcomes, and capability outcomes.
- [x] 6.4 Update stage focus and neutral missing-evidence rules so Control includes approval, Continue includes handoff, and Ground includes grounding without hiding any actual chronological event from the complete record.
- [x] 6.5 Preserve sequential PLAIN-then-HARNESS execution, SSE IDs/order/replay, terminal snapshot reconciliation, TTL cleanup, relative paths, output truncation, and infrastructure-error semantics for all six capabilities.
- [x] 6.6 Add API, store, runner, SSE, catalogue, result, sanitization, and CLI compatibility tests covering all six registered capabilities and the expanded public contracts.

## 7. Add Demo task details and component mapping UI

- [x] 7.1 Extend the experiment API and frontend types to consume server-owned Demo task fields and component relationships with safe missing-data fallbacks.
- [x] 7.2 Add a distinct “查看任务” button to every capability card without changing capability selection, and implement a feature-local modal task dialog showing the experiment question, shared task, two conditions, completion definition, evidence, and talk track.
- [x] 7.3 Implement task dialog labeling, initial focus, focus containment, Escape/close behavior, trigger focus restoration, background interaction blocking, and read-only access while an experiment is running.
- [x] 7.4 Add a compact six-Demo/11-component teaching map that distinguishes primary, supporting, and not-directly-demonstrated relationships in text as well as color and adapts to a vertical mobile layout.
- [x] 7.5 Add component tests for six available cards, selection replacement, opening the correct per-Demo task, missing metadata, keyboard and assistive-technology behavior, focus restoration, mapping accuracy, and narrow-screen content order.

## 8. Present Control, Continue, and Ground evidence

- [x] 8.1 Add typed evidence renderers for approval policy decisions, Session A/B and handoff fields, provider grounding/version/date, loop stop reasons, and task/capability outcome separation.
- [x] 8.2 Extend completed phase comparison for Control action/approval/verification, Continue information/handoff/action/verification, and Ground information/grounding/action/verification with factual neutral placeholders.
- [x] 8.3 Extend conclusion-first summaries and metric rows for the three new capabilities, including controlled rejection, unavailable handoff, missing current policy, infrastructure failure, and non-benchmark qualification.
- [x] 8.4 Complete the inline Control approval states for pending, submitting, approved, rejected, conflict, timeout, disconnect, and recovered experiments without using the task-details modal for approval.
- [x] 8.5 Ensure complete-record filters, copy actions, long evidence, error text, relative paths, focus states, reduced motion, and mobile two-side comparison remain correct for new event kinds and unequal event counts.
- [x] 8.6 Add reducer, component, interaction, accessibility, and responsive tests for successful and unsuccessful Control, Continue, and Ground scenarios and for snapshot/SSE recovery at each new stage.

## 9. Verify and prepare the live demonstration

- [x] 9.1 Run `uv run python -m pytest -q` and `uv run python -m ruff check src tests fixtures` from `backend/` and resolve all deterministic failures without accessing the real network.
- [x] 9.2 Run `npm run lint`, `npm run test`, and `npm run build` from `frontend/` and resolve all type, behavior, accessibility, and build failures.
- [ ] 9.3 Manually inspect all six task dialogs, component mapping, live phases, final summaries, long evidence, and complete records at desktop and mobile widths, including keyboard-only and reduced-motion use.
- [ ] 9.4 Manually exercise Control approval approve/reject/timeout and page refresh, Continue session handoff, and Ground source/version evidence against the local API without exposing secrets or host paths.
- [ ] 9.5 With approved live credentials, rehearse all six PLAIN/HARNESS pairs using a fixed model, provider, code revision, and configuration; record observed variability, duration, and a recommended two-to-three Demo presentation set.
- [ ] 9.6 Prepare bounded fallback screenshots, static diffs, test evidence, or a recording for slow/failed live calls, and ensure fallback material is explicitly labeled separately from the current live run.
- [x] 9.7 Update existing README and practical presenter guidance with Demo 1–6 commands, per-Demo variable/evidence, approval interaction, local-provider wording, one-run qualification, timeout fallback, and the fact that the PPT file remains unchanged.
- [x] 9.8 Verify the original PPT is unmodified, no generated workspace or credential is tracked, all six capability statuses match actual availability, and all resolved Open Questions are reflected consistently across proposal, design, specs, tasks, and UI copy.
