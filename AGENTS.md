# Repository Guidelines

## Project Structure & Module Organization

This repository contains two independent services. `backend/` is a Python 3.12 `uv` project: application modules live in `backend/src/harness_demo/`, deterministic tests in `backend/tests/`, and the synthetic shipping project in `backend/fixtures/shipping/`. Generated demo workspaces belong under `backend/.demo-workspace/`. `frontend/` is a React, TypeScript, and Vite application; place UI code in `frontend/src/` and static assets in `frontend/public/`. Project-level design material lives in `docs/`, while proposals and implementation plans live in `openspec/`.

## Build, Test, and Development Commands

Run commands from the relevant service directory.

```bash
cd backend
uv sync                              # install Python dependencies
uv run harness-demo list             # list demos without calling an LLM
uv run uvicorn harness_demo.web.app:app --host 127.0.0.1 --port 8000  # start stable local API
uv run python -m pytest -q            # run deterministic backend tests
uv run python -m ruff check src tests fixtures

cd frontend
npm install                           # install locked Node dependencies
npm run dev                           # start the Vite development server
npm run lint                          # run Oxlint
npm run build                         # type-check and build production assets
```

## Coding Style & Naming Conventions

Use four-space indentation and `snake_case` for Python functions and modules. Keep lines within Ruff's 100-character limit and retain type annotations. Prefer direct, readable Demo-specific flows over framework-like abstractions. In TypeScript, use two-space indentation, `PascalCase` component names, `camelCase` functions, and strict types; avoid `any`. Keep feature-specific components, API helpers, types, and styles together under `frontend/src/features/<feature>/`.

## Testing Guidelines

Backend tests use pytest and follow `test_*.py` and `test_<behavior>` naming. Tests must use fake Responses clients and must not access the real network or credentials. Add focused tests for CLI control flow, path boundaries, tool validation, and result evaluation. No coverage threshold is configured. For frontend changes, always run lint and build; add UI tests when a test runner is introduced.

## Commit & Pull Request Guidelines

The local history is too sparse to establish a repository-specific convention. Use short, imperative, scoped subjects such as `frontend: add comparison timeline`. Keep unrelated changes separate. Pull requests should explain behavior and tradeoffs, link the relevant OpenSpec change or issue, list verification commands, and include screenshots for visible UI changes.

## Security & Configuration

Copy `backend/.env.example` to `backend/.env`; never commit secrets. Do not expose API keys through `VITE_` variables. Preserve backend restrictions on workspace paths, writable files, fixed test commands, timeouts, and output truncation.
