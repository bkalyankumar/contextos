---
handoff_id: HOFF-0001
task_id: TASK-001
from_agent: chatgpt
to_agent: codex
status: ready
created_at: 2026-05-29
---

# Handoff: ChatGPT -> Codex

## Current Task

Build the local Markdown-first Checkpoint CLI.

## Current Status

Strategy and product direction are settled enough to begin implementation.
A starter repo has been prepared with product context, business plan, MVP spec, architecture notes, tasks, and a minimal Python CLI scaffold.

## Strategic Context

ContextOS is not a generic AI memory product and not another coding agent.
It is a repo-native continuity layer that lets work move across agents without losing architecture, plans, task state, decisions, constraints, or progress.

Core promise:

```text
Plan in Claude. Code in Codex. Debug in Claude Code. Delegate to Antigravity. Resume anywhere.
```

## Immediate Ask For Codex

Start with `TASK-001` and make the CLI usable locally.

## Files To Inspect First

- `AGENTS.md`
- `CODEX_START_PROMPT.md`
- `.contextos/plans/active-plan.md`
- `.contextos/tasks/active/TASK-001.md`
- `docs/mvp-spec.md`
- `docs/technical-architecture.md`
- `src/checkpoint_cli/cli.py`

## Definition Of Done For Next Session

- Package installs.
- CLI help works.
- `checkpoint status` works.
- `checkpoint resume --for codex --task TASK-001` works.
- `checkpoint handoff` writes durable handoff files.
- Tests pass.

## Next Recommended Agent

Codex

## Continuation Prompt

Read `AGENTS.md`, `.contextos/handoffs/latest.md`, and `.contextos/tasks/active/TASK-001.md`. Then implement and test the local Markdown-first Checkpoint CLI. Keep the MVP simple; do not build hosted sync, dashboards, vector search, Tree-sitter, or MCP yet.
