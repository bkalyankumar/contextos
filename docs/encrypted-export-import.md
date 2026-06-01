# Local Encrypted Export / Import Design

## Goal

Let a developer move ContextOS state between machines before hosted sync exists, without introducing a cloud service or hidden database.

The feature should preserve the MVP promise:

```text
Plan in Claude. Code in Codex. Debug in Claude Code. Delegate to Antigravity. Resume anywhere.
```

## Product Boundary

Build later:

- `checkpoint export --output contextos-export.ctx`
- `checkpoint import contextos-export.ctx`
- passphrase-protected local archive
- manifest with schema version, created time, project identity, and included files
- dry-run import preview
- explicit overwrite/merge prompts

Do not build in the MVP design:

- hosted sync
- accounts
- device pairing
- background daemon
- vector index transfer
- enterprise policy controls

## Archive Contents

Default export should include only human-readable continuity state:

- `.contextos/context/`
- `.contextos/plans/`
- `.contextos/tasks/`
- `.contextos/handoffs/`
- `.contextos/agents/`
- `.contextos/state/events.jsonl`
- `AGENTS.md`
- `CLAUDE.md`

Default export should exclude generated or future-heavy state:

- `.contextos/state/index.sqlite`
- `.contextos/state/embeddings/`
- virtual environments
- dependency caches
- repository source files
- secrets, tokens, credentials, and private key material

## Security Model

Use authenticated encryption, not a hand-rolled cipher.

Recommended implementation:

- Python `cryptography`
- Argon2id or PBKDF2-HMAC-SHA256 key derivation
- random per-export salt
- random nonce
- AES-256-GCM or ChaCha20-Poly1305
- manifest authenticated as additional data

The passphrase is never written to disk, never logged, and never stored in events.

## Secret Handling

Before packaging, run the same redaction scanner used for generated continuation packs against included Markdown files.

If likely secrets are found:

1. fail closed by default,
2. print file paths and redacted detector labels,
3. suggest removing the secret from ContextOS state,
4. allow a future explicit `--allow-secrets` only after the UX has a clear warning.

## Import Semantics

Import should be conservative:

- verify archive authentication before writing anything,
- render a dry-run summary by default,
- refuse to overwrite existing files unless `--overwrite` is passed,
- preserve existing handoff history unless merge behavior is explicit,
- append an `import.completed` event with archive metadata only, never file contents.

## Failure Modes

Named failures should map to clear user actions:

- `ExportSecretFoundError`: remove or redact the reported secret source.
- `ExportWriteError`: choose a writable output path.
- `ImportAuthenticationError`: check passphrase or archive integrity.
- `ImportConflictError`: rerun with `--overwrite` or import into a clean checkout.
- `ImportSchemaError`: upgrade Checkpoint or use a compatible export.

## CLI Sketch

```bash
checkpoint export --output ~/contextos-project.ctx
checkpoint export --output ~/contextos-project.ctx --include-user
checkpoint import ~/contextos-project.ctx --dry-run
checkpoint import ~/contextos-project.ctx --overwrite
```

## Event Log

Events should include metadata only:

```json
{"type":"export.created","schema_version":1,"output":"...","files":17}
{"type":"import.completed","schema_version":1,"files":17,"overwrite":false}
```

## Open Questions For Implementation

- Whether user-level `~/.contextos/about-me.md` belongs in default export or requires `--include-user`.
- Whether imports should merge task directories by filename or require an empty target.
- Whether encrypted exports should be portable across OS path conventions.

## Decision

For the MVP, keep this as a design artifact and do not add a cryptography dependency yet. Implement encrypted export/import after the Markdown-first local loop is validated and the CLI has enough users to justify the extra dependency and migration surface.
