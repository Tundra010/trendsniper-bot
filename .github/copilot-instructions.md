## Quick context

Repository state (checked on 2025-10-12): empty — no source files were present when this guidance was generated. The instructions below are tailored to this workspace: they explain how an AI coding agent should discover the project structure, what files to read first, and how to merge/update these instructions once sources appear.

## Primary goal for an AI agent

Be immediately productive by: (1) discovering the project's language, entry points, and package/CI manifests, (2) identifying build/test commands from manifests, (3) locating integration points (infra, Docker, CI), and (4) making minimal, low-risk edits (docs, scripts, tests) while preserving existing patterns.

## Concrete discovery checklist (run in order)

1. Look for repository manifests at the repo root and read them to learn build/test commands:
   - `package.json` (npm/yarn/pnpm) — read `scripts` and `engines`
   - `pyproject.toml`, `requirements.txt`, `setup.cfg`, `setup.py` (Python)
   - `go.mod` (Go), `pom.xml` (Maven/Java)
   - `Cargo.toml` (Rust)
   - `Pipfile`, `Gemfile`, `Makefile`, `Dockerfile`

2. If a `README.md` exists, extract the quickstart and development commands. Prioritize commands there over guesses.

3. Inspect CI/workflows in `.github/workflows/*.yml` for test/build steps and environment secrets referenced.

4. Identify entrypoints and major components by scanning common directories:
   - `src/`, `app/`, `server/`, `services/`, `cmd/`, `pkg/`, `backend/`, `frontend/`
   - Look for files named `main.*`, `server.*`, `index.*`, `app.*`, `handler.*`

5. Search for infra/config patterns: `Dockerfile`, `docker-compose.yml`, `k8s/`, `terraform/`, `cloudbuild/`, `sam.yml`.

6. Note environment/config conventions: `.env`, `config/*.yaml|json|toml`, `secrets`, or references to secret stores.

## How to update this file (merge rules)

- If this file already exists, preserve any human-written bullets. When adding new content, append a small section with the date and a 1-line summary of what changed.
- When merging automated findings, always quote the exact manifest line you relied on (e.g., `scripts.test` from `package.json`) so humans can verify decisions.

## Project-specific guidance (when sources appear)

- Prefer reading manifest scripts over guessing commands. Examples:
  - If `package.json` contains `"dev": "vite"`, use `npm run dev` rather than assuming `npm start`.
  - If `pyproject.toml` defines `tool.poetry`, use `poetry install`/`poetry run` flows.

- When modifying code, follow existing file-level patterns exactly: match import style (relative vs absolute), error handling style (exceptions vs return codes), and formatting used in the repository; reference the nearest similar file as example.

- For feature work, prefer editing or adding tests adjacent to the changed code. Locate test framework by files under `test/` or `tests/`, or by dev-dependencies in manifests.

## Quick examples (what to look for)

- Finding the start command: open `package.json` -> read `scripts.start` or `scripts.dev`.
- Finding Docker build args: open `Dockerfile` -> look for `ENV`, `EXPOSE`, and `CMD` lines to understand runtime.
- Locating CI secrets: open `.github/workflows/*` and note `secrets` keys used (e.g., `GITHUB_TOKEN`, `DOCKERHUB_USERNAME`).

## Safety and low-risk defaults

- If uncertain about running build/test commands, prefer read-only analysis (opening manifests and CI files) and suggest commands to a human.
- Avoid pushing changes that modify infra or CI without a small, explicit test and a matching CI workflow update.

## What to include in PRs created by an agent

- A short description of discovery steps and the exact manifest lines relied upon.
- A minimal test or smoke command that proves the change compiles or lints (if applicable).

## When you can't find anything

This repository had no source files when inspected. If you reach this state:

1. Create or update `README.md` with the intended language and quickstart.
2. Create a minimal manifest for the chosen language (e.g., `package.json` with `scripts` or `pyproject.toml`) so future agents can detect tooling.

---
If any of the above is unclear or you'd like the instructions tailored to a specific language or project structure, tell me which language/framework to prioritize and I'll iterate.
