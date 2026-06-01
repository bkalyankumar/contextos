# Constraints

## Product constraints

- Local-first by default.
- Repo-native project memory.
- Tool-agnostic agent handoff.
- Markdown-readable MVP.
- Compression over raw context dumps.
- Do not build an agent runtime in the MVP.

## Technical constraints

- Python CLI with Typer.
- Avoid unnecessary dependencies.
- Use plain files first.
- Keep generated files deterministic where possible.
- Never store secrets in handoff/context files.
- All future remote sync must be encrypted before upload.

## Business constraints

- Do not monetize the basic local habit loop.
- Open-source the schema and local CLI.
- Monetize encrypted sync, team memory, and enterprise governance.
