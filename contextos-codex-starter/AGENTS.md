# AGENTS.md - ContextOS Project Instructions

This repository uses ContextOS-style persistent engineering memory.

## Role

You are helping build ContextOS and Checkpoint.

ContextOS is repo-native, tool-agnostic continuity infrastructure for AI-assisted software engineering.
Checkpoint is the CLI for creating, updating, and projecting that shared context into the next AI coding tool.

## Always read before work

1. `.contextos/handoffs/latest.md`
2. `.contextos/plans/active-plan.md`
3. `.contextos/context/project-summary.md`
4. `.contextos/context/architecture.md`
5. `.contextos/context/constraints.md`
6. Relevant task file under `.contextos/tasks/active/`

## Product principle

The product is not another coding agent.
It is the continuity layer beneath coding agents.

Core promise:

```text
Plan in Claude. Code in Codex. Debug in Claude Code. Delegate to Antigravity. Resume anywhere.
```

## MVP scope

Build now:

- local-first Markdown memory
- user-level `about-me.md` template
- project-level `.contextos/` files
- `checkpoint init`
- `checkpoint setup-user`
- `checkpoint status`
- `checkpoint resume`
- `checkpoint handoff`
- generated `AGENTS.md` and `CLAUDE.md`
- durable task files
- durable handoff files

Do not build yet:

- hosted cloud platform
- dashboard
- IDE extension
- vector database
- Tree-sitter indexing
- multi-agent runtime
- enterprise governance
- agent marketplace

## Engineering style

- Keep the first implementation boring and reliable.
- Prefer readable Markdown over hidden state.
- Prefer explicit files over magical behavior.
- Do not introduce dependencies unless they materially simplify the MVP.
- Use Typer for the CLI.
- Keep all context files human-readable.
- Never store secrets, API keys, tokens, or private credentials in generated handoffs.

## Handoff requirement

Before ending work, update:

- `.contextos/handoffs/latest.md`
- the relevant task file in `.contextos/tasks/active/`
- `.contextos/context/decisions.md` if a durable decision was made

Every handoff must include:

- current task
- current status
- files changed
- tests run
- blockers
- decisions
- next recommended agent
- exact continuation prompt
