# Changelog

All notable changes to Checkpoint are recorded here.

## Unreleased

- Refreshed public launch README positioning and source-install path.
- Added security policy, code of conduct, and public launch checklist.
- Added public package metadata to `pyproject.toml`.

## 0.1.0 - 2026-06-01

- Added the local-first Checkpoint CLI scaffold.
- Added `checkpoint setup-user`, `init`, `status`, `resume`, `continue`, `handoff`, `detect-agent`, and `show`.
- Added agent-specific context packs for Claude, Codex, Claude Code, Antigravity, and generic fallback.
- Added durable Markdown handoffs, append-only local events, and secret redaction for generated context.
- Added the local encrypted export/import design in `docs/encrypted-export-import.md`; implementation remains deferred.

## Migration Notes

- No migrations are required for `0.1.0`.
- The project is still pre-release. Generated `.contextos/` files are Markdown and can be reviewed or edited directly.
