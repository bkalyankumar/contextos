# TASK-003: Add encrypted export/import design

## Status

Design complete. Implementation intentionally deferred until after the Markdown-first local loop is validated.

## Recommended Agent

Claude for design, Codex for implementation later

## Goal

Design and later implement local encrypted export/import so context can move between machines before hosted sync exists.

## Out of Scope For Now

Hosted Context Vault.

## Design Artifact

`docs/encrypted-export-import.md`

## Design Notes

- Export/import remains local-first and file-based.
- The archive should include ContextOS continuity files, not repository source files or generated indexes.
- Implementation must use authenticated encryption through a real cryptography library, not a hand-rolled cipher.
- Exports should scan for likely secrets and fail closed by default.
- Imports should verify authentication before writing, dry-run by default, avoid accidental overwrite, and log metadata-only events.
- User-level context export remains an open implementation question and should require explicit user intent.

## Verification

- Design linked from `docs/technical-architecture.md`.
- Roadmap updated to record encrypted export/import design as complete while keeping implementation out of the current MVP.
