# TASK-001: Build local Markdown-first Checkpoint CLI

## Status

Ready for Codex implementation.

## Recommended Agent

Codex

## Goal

Turn the starter scaffold into a working local-first CLI that can initialize project memory, report status, generate resume context packs, and write handoffs.

## Scope

Implement or harden:

- `checkpoint setup-user`
- `checkpoint init`
- `checkpoint status`
- `checkpoint resume`
- `checkpoint handoff`

## Constraints

- Keep MVP local-only.
- Use Markdown files as the source of truth.
- Do not build cloud sync.
- Do not add vector search.
- Do not add Tree-sitter yet.
- Do not add dashboard/IDE extension.
- Do not store secrets.

## Relevant Files

- `src/checkpoint_cli/cli.py`
- `src/checkpoint_cli/store.py`
- `src/checkpoint_cli/templates.py`
- `AGENTS.md`
- `.contextos/handoffs/latest.md`
- `tests/test_cli.py`

## Definition of Done

- `pip install -e '.[dev]'` succeeds.
- `checkpoint --help` works.
- `checkpoint init` creates expected files without overwriting existing files.
- `checkpoint status` summarizes project state.
- `checkpoint resume --for codex --task TASK-001` emits useful context.
- `checkpoint handoff --from codex --to claude-code --task TASK-001 --status in_progress` writes latest and timestamped handoffs.
- Tests pass.

## Handoff Instructions

At the end, update this task status and write `.contextos/handoffs/latest.md` with what changed, files touched, tests run, blockers, decisions, next recommended agent, and continuation prompt.
