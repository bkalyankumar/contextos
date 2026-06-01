# TASK-001: Build local Markdown-first Checkpoint CLI

## Status

Implemented and verified in the first Codex pass. Ready for follow-up review or the next MVP task.

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

- `pip install -e '.[dev]'` succeeds in a throwaway venv.
- `checkpoint --help` works.
- `checkpoint init` creates expected files without overwriting existing files.
- `checkpoint status` summarizes project state.
- `checkpoint resume --for codex --task TASK-001` emits useful context and preserves raw Markdown text such as `.[dev]`.
- `checkpoint handoff --from codex --to claude-code --task TASK-001 --status in_progress` writes latest and timestamped handoffs.
- Tests pass.

## Codex Implementation Notes

- Scoped pytest to the top-level `tests/` directory so the nested starter copy is not collected.
- Made resume/show output write raw Markdown instead of Rich markup-rendered text.
- Added ordered resume sections for current task, blocker, constraints, plan, architecture, relevant files, recent handoff, next action, and handoff instructions.
- Made handoff filenames unique with microsecond timestamps.
- Added a small handoff redaction pass for common token/secret/password forms.
- Expanded CLI tests for setup-user/init, status, resume, handoff durability, event logging, no-overwrite behavior, and raw `.[dev]` preservation.

## Verification

- `pip` was not on PATH and `pip3 install -e '.[dev]'` was blocked by Homebrew's externally managed Python policy.
- Created `/private/tmp/contextos-checkpoint-venv` and verified install with `/private/tmp/contextos-checkpoint-venv/bin/pip install -e '.[dev]'`.
- Ran `/private/tmp/contextos-checkpoint-venv/bin/checkpoint --help`.
- Ran `/private/tmp/contextos-checkpoint-venv/bin/checkpoint status`.
- Ran `/private/tmp/contextos-checkpoint-venv/bin/checkpoint resume --for codex --task TASK-001`.
- Ran `/private/tmp/contextos-checkpoint-venv/bin/pytest` with `4 passed`.

## Handoff Instructions

At the end, update this task status and write `.contextos/handoffs/latest.md` with what changed, files touched, tests run, blockers, decisions, next recommended agent, and continuation prompt.
