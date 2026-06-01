# TASK-002: Add agent-specific context packs

## Status

Implemented and verified in Codex.

## Recommended Agent

Codex or Claude Code

## Goal

Make `checkpoint resume --for <agent> --mode <mode>` produce role-specific context packs.

## Target agents

- Claude planning pack
- Codex implementation pack
- Claude Code debug pack
- Antigravity autonomous task pack

## Definition of Done

Each target agent gets a context pack optimized for its role, not a generic wall of notes.

## Implementation Notes

- Added agent-specific resume pack profiles for Claude, Codex, Claude Code, and Antigravity in `src/checkpoint_cli/store.py`.
- `checkpoint resume --for <agent> --mode <mode>` now includes an `Agent-Specific Pack` section with pack name, requested mode, work focus, context priority, and stop conditions.
- Unknown agents still receive a generic continuation-safe pack.
- Added tests that verify each target agent emits distinct role-specific pack content.

## Verification

- `.venv/bin/pytest` passed with agent-specific pack coverage.
