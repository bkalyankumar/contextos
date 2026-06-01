# Decisions

## DEC-001: ContextOS should not position as generic AI memory

Reason: generic memory is already being claimed by products such as Mem0 and by tool-native memory features.

Decision: ContextOS positions as repo-native continuity infrastructure for AI-assisted software engineering.

## DEC-002: MVP is Markdown-first

Reason: readable files support trust, git workflows, portability, and easy agent consumption.

Decision: initial source of truth is `.contextos/` Markdown plus generated `AGENTS.md` / `CLAUDE.md`.

## DEC-003: Open-source local CLI and schema

Reason: adoption depends on becoming a standard local habit.

Decision: paid features begin at encrypted sync, teams, and governance.

## DEC-004: Agent handoff through ContextOS, not direct agent-to-agent memory

Reason: direct transfer between agents is brittle and vendor-specific.

Decision: each agent reads/writes canonical ContextOS state.
