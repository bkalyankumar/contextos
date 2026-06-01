# ContextOS / Checkpoint

ContextOS is repo-native continuity infrastructure for AI-assisted software
engineering. Checkpoint is the local CLI that creates, updates, and projects
that context into the next AI coding tool.

```text
Plan in Claude -> Code in Codex -> Debug in Claude Code -> Delegate to Antigravity -> Resume anywhere
```

Checkpoint is not another coding agent. It is the continuity layer beneath
coding agents: readable Markdown memory, durable task files, durable handoffs,
and agent-specific continuation packs.

## Status

Checkpoint is pre-1.0 and ready for early open-source contributors. The current
release proves the local-first workflow; cloud sync, dashboards, IDE extensions,
vector search, and hosted agent runtimes are intentionally out of scope.

## What It Does

- Creates project memory in `.contextos/`
- Creates user memory in `~/.contextos/about-me.md`
- Generates `AGENTS.md` and `CLAUDE.md` compatibility files
- Tracks active tasks, completed tasks, decisions, and handoffs
- Emits Markdown continuation packs for Codex, Claude, Claude Code,
  Antigravity, Cursor, or a generic agent
- Redacts common secret patterns before generated continuation output
- Logs local continuity events without storing generated pack contents

## How It Works

ContextOS uses a local Markdown store plus agent-specific projections:

```text
Local Markdown Store
  -> Projection Engine
  -> Continuation Pack
  -> Agent-specific Handoff
```

Project memory lives in the repository:

```text
repo/.contextos/
  context/
  plans/
  tasks/
  handoffs/
  agents/
  state/events.jsonl
```

User memory lives outside the repository:

```text
~/.contextos/about-me.md
```

Projection files make existing tools understand the same continuity layer:

```text
AGENTS.md
CLAUDE.md
```

## Install

Install the packaged CLI:

```bash
pip install checkpoint-cli
```

With uv:

```bash
uv tool install checkpoint-cli
```

Then verify the CLI:

```bash
checkpoint --help
checkpoint status
checkpoint continue
```

## Install From Source

```bash
git clone git@github.com:bkalyankumar/contextos.git
cd contextos
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Smoke test:

```bash
checkpoint --help
checkpoint status
checkpoint continue
```

Editable install from a source checkout remains the recommended path for
contributors.

## First Run In A Project

```bash
checkpoint setup-user
checkpoint init
checkpoint status
checkpoint continue
```

`checkpoint continue` is the happy path. It detects the current agent when it
can, reads the latest handoff and active task, and prints a Markdown continuation
pack with inference provenance.

Useful overrides:

```bash
checkpoint continue --output /tmp/contextos-pack.md
checkpoint detect-agent
```

After a handoff and task file exist, you can pin the source handoff, target
agent, or task explicitly:

```bash
checkpoint continue --from claude
checkpoint continue --from codex --for claude-code --task TASK-001
```

Lower-level primitives remain available when you want direct control:

```bash
checkpoint resume --for codex --task TASK-001
checkpoint handoff --from codex --to claude-code --task TASK-001 --status in_progress
checkpoint show .contextos/handoffs/latest.md
```

## Repository Layout

```text
src/checkpoint_cli/        Python CLI implementation
tests/                     CLI and resolver tests
.github/                   CI, issue templates, PR template
```

Generated ContextOS state in consuming projects is plain Markdown by design.
You should be able to review it, edit it, diff it, and commit it like any other
repo-native project file.

This repository dogfoods ContextOS locally, but its own `.contextos/` state is
kept out of git so agent handoffs, working plans, and internal references do not
become part of the public open-core history.

Public product information intentionally lives in this README and the release
history. Longer internal docs, planning notes, launch notes, and reference
material are kept local or in private repositories.

## Current Scope

Built now:

- local-first Markdown memory
- `checkpoint setup-user`
- `checkpoint init`
- `checkpoint status`
- `checkpoint resume`
- `checkpoint handoff`
- `checkpoint continue`
- `checkpoint detect-agent`
- `checkpoint show`
- agent-specific continuation packs
- local event logging
- final redaction for generated continuation output
- Apache-2.0 open-core CLI and schema

Intentionally out of scope for the current open-core CLI:

- hosted cloud platform
- dashboard
- IDE extension
- hosted agent runtime
- Tree-sitter indexing
- vector database
- multi-agent runtime
- enterprise governance

## Roadmap

Next likely open-core improvements:

- generated `AGENTS.md` and `CLAUDE.md`
- conflict-safe handoff history
- clearer CLI recovery messages
- more redaction coverage
- better examples for real agent-switch workflows

Future private/commercial surfaces:

- encrypted hosted sync
- team shared memory
- device pairing
- admin and governance controls
- audit and enterprise features

## Future Sync Design

Before any hosted sync, ContextOS should support a passphrase-protected local
export/import archive for moving continuity state between machines. That future
feature should use authenticated encryption, scan included Markdown for likely
secrets, fail closed by default, and log only metadata events.

Hosted sync remains out of scope for the open-core MVP and must be encrypted
before upload.

## Verification

Run the full local health stack:

```bash
mypy src
ruff check .
pytest
vulture src tests
```

The same checks run in CI.

## Privacy And Safety

- ContextOS is local-first by default.
- Generated handoffs must not contain secrets, API keys, tokens, or private
  credentials.
- `checkpoint continue` applies final redaction before printing or writing a
  continuation pack.
- Local event logs store command metadata, not generated continuation pack text.
- Future remote sync must be encrypted before upload.

Security reports should follow [SECURITY.md](SECURITY.md), not public issues.

## Contributing

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Good first contributions improve
the local-first CLI, documentation, examples, tests, and failure messages.

Please keep the MVP boring and reliable:

- Prefer readable Markdown over hidden state.
- Prefer explicit files over magical behavior.
- Do not add hosted sync, dashboards, IDE extensions, vector databases,
  Tree-sitter indexing, or multi-agent runtimes to the MVP.
- Update tests and docs with behavior changes.

## License

Checkpoint is licensed under the [Apache License 2.0](LICENSE).
