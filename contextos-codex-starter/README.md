# ContextOS / Checkpoint MVP Starter

ContextOS is a repo-native continuity layer for AI-assisted software engineering.
Checkpoint is the CLI that lets work move across agents without losing architecture, plans, decisions, task state, implementation progress, or handoff history.

Core workflow:

```text
Plan in Claude -> Code in Codex -> Debug in Claude Code -> Delegate to Antigravity -> Resume anywhere
```

This starter repo contains:

- a minimal Python + Typer CLI scaffold for `checkpoint`
- repo-level `AGENTS.md` and `CLAUDE.md` instructions
- `.contextos/` canonical project memory
- business plan, MVP spec, monetization plan, and technical architecture
- Codex-ready handoff prompt and task list

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
checkpoint --help
checkpoint status
checkpoint resume --for codex --task TASK-001
```

## Recommended Codex start

Open this repo in Codex and paste the contents of:

```text
CODEX_START_PROMPT.md
```

Codex should first read:

```text
AGENTS.md
.contextos/handoffs/latest.md
.contextos/plans/active-plan.md
.contextos/tasks/active/TASK-001.md
```

## Product promise

After initial setup, every coding agent should know:

- who the user is and how they work
- what this project is
- what the current plan is
- what task is active
- what changed in the previous agent session
- which constraints must not be violated
- which agent should receive the next handoff

## Current MVP boundary

Build local-first first:

- local Markdown state
- local task and handoff files
- generated `AGENTS.md` / `CLAUDE.md`
- basic `checkpoint init`, `status`, `handoff`, and `resume`
- no hosted sync yet
- no dashboard yet
- no IDE extension yet
- no multi-agent runtime yet
