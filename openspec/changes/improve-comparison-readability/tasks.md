## 1. Backend presentation contracts

- [x] 1.1 Extend the public event and result models with stage-specific bounded evidence, per-run objective facts, and capability-specific comparison rows while preserving existing event identity and ordering fields.
- [x] 1.2 Introduce a small typed Demo reporter with console and Web/store sinks so one semantic operation can drive both CLI output and API events.
- [x] 1.3 Centralize construction, path normalization, sanitization, and truncation for model output, tool results, Diff, test evidence, and infrastructure errors.
- [x] 1.4 Add deterministic comparison builders for Understand, Act, and Prove that use recorded facts, qualify conclusions as one-run observations, and distinguish analysis, proposal, verification failure, and infrastructure failure.

## 2. Semantic Demo event production

- [x] 2.1 Adapt Demo 1 to report input sources, one bounded model-analysis event, structured analysis checks, unchanged-workspace evidence, and an analysis terminal result without splitting answer lines.
- [x] 2.2 Adapt Demo 2 to report proposal output or bounded read/write/test operations, modified files, Diff, scope checks, and the terminal evaluation as semantic events.
- [x] 2.3 Adapt Demo 3 to report each generation, write, test, feedback transition, final Diff, call count, and terminal evaluation while keeping test source hidden from the model.
- [x] 2.4 Replace the Web runner's stdout line classifier with the typed Web reporter, retain sequential PLAIN-to-HARNESS execution, and populate the enriched final snapshot after both sides finish.
- [x] 2.5 Preserve the existing CLI labels and readable bounded output for Demo 1–3 through the console sink, including proposal-only and expected analysis outcomes.

## 3. Backend verification

- [x] 3.1 Add model and reporter tests proving that each operation emits one ordered event and that multiline model, Diff, and test content remains attached as bounded evidence.
- [x] 3.2 Add focused adapter tests for the Understand context/check metrics, Act proposal/action metrics, and Prove generation/test/feedback metrics and causal ordering.
- [x] 3.3 Add comparison-builder tests for readable outcome semantics, non-benchmark qualification, missing evidence, and single-side infrastructure failures.
- [x] 3.4 Update store, SSE replay, terminal snapshot, sanitization, path boundary, and CLI compatibility tests for the enriched event contract.
- [x] 3.5 Run `uv run python -m pytest -q` and `uv run python -m ruff check src tests fixtures` from `backend/`.

## 4. Frontend explanatory comparison

- [x] 4.1 Replace generic evidence and snapshot types with discriminated stage evidence, objective run facts, and typed comparison-summary contracts without weakening strict TypeScript checks.
- [x] 4.2 Build a conclusion-first summary that displays the one-run observation, readable PLAIN/HARNESS outcomes, capability-specific metric rows, and the non-benchmark qualification before detailed process content.
- [x] 4.3 Build a stable phase model that always shows information and conclusion, adds Act action/verification and Prove action/verification/feedback focus phases, includes any other phase with actual events, and omits unrelated phases empty on both sides.
- [x] 4.4 Keep the live view concise with one card per semantic event and transition it to the completed phase comparison without losing streamed or recovered events.
- [x] 4.5 Replace generic JSON evidence with stage-specific labeled fields, safe Diff/log presentation, bounded scrolling, empty-evidence fallbacks, and copy actions.
- [x] 4.6 Add a collapsed same-page complete-record region after the explanatory content, with sequence-ordered events, explicit side labels, All/PLAIN/HARNESS filters, wide evidence presentation, and no drawer, modal, or separate route.
- [x] 4.7 Implement responsive phase cards that keep both sides visible on small screens, render factual neutral placeholders for missing phase evidence, and ensure outcomes, expansion controls, focus states, and differences are not communicated by color alone.

## 5. Frontend verification and documentation

- [x] 5.1 Add reducer and component tests for streamed event ordering, snapshot recovery, conclusion placement, capability-specific phase visibility, unrelated empty-phase omission, and neutral missing-side labels with unequal PLAIN/HARNESS event counts.
- [x] 5.2 Add scenario tests for Understand analysis, Act proposal versus verified action, Prove fail-feedback-fix-pass, infrastructure failure, missing evidence, and long output.
- [x] 5.3 Add interaction and accessibility tests for typed evidence drawers, same-page complete-record disclosure and side filters, focus return, keyboard use, mobile comparison content, and reduced-motion behavior.
- [x] 5.4 Update the backend/frontend README descriptions of Web event presentation and result interpretation where the public contract or operator workflow materially changes.
- [ ] 5.5 Run `npm run lint`, `npm run test`, and `npm run build` from `frontend/`, then manually inspect the three available Demo layouts at desktop and mobile widths.
