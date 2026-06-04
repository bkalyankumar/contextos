# ContextOS / Checkpoint

[![PyPI](https://img.shields.io/pypi/v/checkpoint-cli.svg)](https://pypi.org/project/checkpoint-cli/)
[![Python](https://img.shields.io/pypi/pyversions/checkpoint-cli.svg)](https://pypi.org/project/checkpoint-cli/)
[![License](https://img.shields.io/pypi/l/checkpoint-cli.svg)](LICENSE)
[![CI](https://github.com/bkalyankumar/contextos/actions/workflows/ci.yml/badge.svg)](https://github.com/bkalyankumar/contextos/actions/workflows/ci.yml)

ContextOS is repo-native continuity infrastructure for AI-assisted software
engineering. Checkpoint is the local CLI that captures, updates, and projects
that context into the next AI coding tool.

```text
Plan in Claude -> Code in Codex -> Debug in Claude Code -> Delegate to Antigravity -> Resume anywhere
```

Checkpoint is not another coding agent. It is the continuity layer beneath
coding agents: readable Markdown memory, durable task files, durable handoffs,
and agent-specific continuation packs.

[Install](#install) |
[Quickstart](#60-second-quickstart) |
[Commands](#commands) |
[How It Works](#how-it-works) |
[Scope](#current-scope) |
[Contributing](#contributing)

## Why Checkpoint?

AI coding sessions are powerful, but continuity is fragile. Important context
lives in chat history, one tool's private memory, or a local scratch note that
the next agent cannot see.

Checkpoint gives a repository an explicit continuity layer:

- Human-readable project memory in `.contextos/`
- User preferences in `~/.contextos/about-me.md`
- Durable active tasks, completed tasks, decisions, and handoffs
- Generated `AGENTS.md` and `CLAUDE.md` compatibility files
- Continuation packs for Codex, Claude, Claude Code, Antigravity, Cursor, or a
  generic agent
- Final redaction for common secret patterns before generated continuation
  output is printed or written

The goal is simple: make the next agent useful in the first minute.

## Install

Install the packaged CLI:

```bash
pip install checkpoint-cli
```

Or install it as a uv tool:

```bash
uv tool install checkpoint-cli
```

Verify the command:

```bash
checkpoint --help
```

## 60-Second Quickstart

Run this inside any project that should remember its agent work:

```bash
checkpoint setup-user
checkpoint init
checkpoint status
checkpoint continue
```

Or run the tiny demo flow from a source checkout:

```bash
CHECKPOINT_BIN=.venv/bin/checkpoint bash examples/checkpoint-demo.sh
```

The demo creates a temporary project, seeds meaningful local Markdown context,
records a Claude-to-Codex handoff, and prints a Codex continuation pack.

Typical `checkpoint status` output:

```text
                        ContextOS Status
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Item           ┃ Status                      ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Project root   │ /path/to/your/repo          │
│ .contextos     │ yes                         │
│ AGENTS.md      │ yes                         │
│ CLAUDE.md      │ yes                         │
│ Latest handoff │ yes                         │
│ Active tasks   │ 0                           │
└────────────────┴─────────────────────────────┘
```

`checkpoint continue` works even before the first task exists, so a new agent
can start from project memory and leave the first durable handoff. After a task
and handoff exist, it becomes the happy path: it detects the current agent when
it can, reads the latest handoff and active task, and prints a Markdown
continuation pack with inference provenance.

```bash
checkpoint continue --for claude-code
```

Example continuation pack shape:

```markdown
# ContextOS Continuation Pack

## Target Agent

claude-code

## Current Task

TASK-001: Add checkpoint status

## Latest Handoff

Status: in_progress
Next: finish tests, then update README

## Continue From Here

Read AGENTS.md, inspect the active task file, run the focused tests, and keep
the handoff current before ending the session.
```

Write the pack to a file when you want to paste, attach, or inspect it later:

```bash
checkpoint continue --for codex --output /tmp/contextos-pack.md
```

When work ends, finalize the execution so the next agent starts from what
actually happened:

```bash
checkpoint finalize --from codex --to claude-code --task TASK-001 \
  --status success \
  --summary "Implemented the parser fix" \
  --files "src/parser.py,tests/test_parser.py" \
  --tests "pytest tests/test_parser.py passed" \
  --next-action "Debug the remaining edge case in Claude Code"
```

## Commands

| Command | Use it when you want to |
| --- | --- |
| `checkpoint setup-user` | Create or update your user-level `about-me.md` |
| `checkpoint init` | Add ContextOS files to the current project |
| `checkpoint status` | See whether project memory, tasks, and handoffs exist |
| `checkpoint continue` | Generate the next-agent continuation pack |
| `checkpoint resume` | Build a lower-level resume pack for a specific agent |
| `checkpoint handoff` | Record a handoff between agents |
| `checkpoint finalize` | Close out work with execution evidence, memory updates, and a handoff |
| `checkpoint history` | Inspect recent local ContextOS events |
| `checkpoint memory` | List or search local failure, strategy, and area memory |
| `checkpoint doctor` | Diagnose continuity health and stale or missing state |
| `checkpoint view` | Generate Markdown and Mermaid continuity reports |
| `checkpoint guard` | Check continuity quality before startup, edits, final answers, or finalize |
| `checkpoint steer` | Classify user interruptions during active work |
| `checkpoint map` | Refresh, inspect, and query the local RepoMap |
| `checkpoint mcp-server` | Expose continuity through an optional local MCP server |
| `checkpoint detect-agent` | Show the agent Checkpoint inferred from the environment |
| `checkpoint show <path>` | Print a ContextOS file with safe path handling |

Useful overrides:

```bash
checkpoint continue --from codex
checkpoint continue --from codex --for claude-code --task TASK-001
checkpoint resume --for cursor --task TASK-001
checkpoint handoff --from codex --to claude-code --task TASK-001 --status in_progress
checkpoint finalize --from codex --task TASK-001 --status success --summary "Done"
checkpoint finalize --summary "Done" --changed "src/parser.py" --test "pytest passed"
checkpoint history
checkpoint memory list
checkpoint memory search "parser failure"
checkpoint doctor --json
checkpoint view
checkpoint map refresh
checkpoint map query "parser tests"
checkpoint show .contextos/handoffs/latest.md
```

## How It Works

Checkpoint uses a local Markdown store plus agent-specific projections:

```text
repo/.contextos/
  context/
    architecture.md
    constraints.md
    decisions.md
    project-summary.md
  plans/
    active-plan.md
  tasks/
    active/
    completed/
  handoffs/
    latest.md
  memory/
    failures.jsonl
    strategies.jsonl
    areas.json
  repo-map/
    manifest.json
    index.json
    status.json
  reports/
    continuity-view.md
    continuity-map.mmd
  agents/
  state/
    events.jsonl
    latest-contract.json
    latest-execution-summary.md
    contract-compliance.jsonl

~/.contextos/
  about-me.md
```

The projection flow is intentionally boring:

```text
Local Markdown Store
  -> Checkpoint resolver
  -> Execution contract
  -> Secret redaction
  -> Continuation Pack
  -> Next coding agent
```

`checkpoint finalize` records observed evidence after work: handoff state,
active task runtime state, execution summary, failure memory, strategy memory,
area memory, and audit-only contract compliance. Contracts are guidance and
quality signals, not sandboxing or enforcement.

For the common single-task case, `checkpoint finalize` can infer the current
agent and task:

```bash
checkpoint finalize --summary "Fixed parser edge case" --changed "src/parser.py" --test "pytest passed"
```

`checkpoint map refresh` builds a lightweight stdlib RepoMap from paths, Python
symbols, README/docs headings, and config files. It is intentionally useful
before it is fancy: no Tree-sitter, no vector database, and no hidden service.

`checkpoint history` and `checkpoint memory` make the runtime inspectable after
it starts recording events, failures, strategies, and area summaries.

Generated compatibility files make existing tools understand the same
continuity layer:

```text
AGENTS.md
CLAUDE.md
```

Everything important is plain text by design. You can review it, edit it, diff
it, and commit the project memory that belongs in your repository.

## Repository Layout

```text
src/checkpoint_cli/        Python CLI implementation
tests/                     CLI and resolver tests
.github/                   CI, issue templates, PR template
```

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
- generated `AGENTS.md` and `CLAUDE.md`
- durable task files
- durable handoff files
- agent-specific continuation packs
- local event logging
- `checkpoint finalize` execution closeout
- `checkpoint history`
- `checkpoint memory list/search`
- failure memory and strategy memory
- audit-only execution contracts and compliance signals
- Markdown and Mermaid continuity reports
- continuity diagnostics with `checkpoint doctor`
- continuity guard and steer helpers
- stdlib RepoMap refresh/status/query
- optional local MCP server via `checkpoint-cli[mcp]`
- final redaction for generated continuation output
- Apache-2.0 open-core CLI and schema

## Roadmap

Next likely open-core improvements:

- conflict-safe handoff history
- clearer CLI recovery messages
- more redaction coverage
- better examples for real agent-switch workflows
- richer command output without hiding the underlying Markdown files
- optional richer RepoMap providers once the stdlib index proves useful

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

Security reports should follow [SECURITY.md](SECURITY.md), not public issues.

## Contributing

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Good first contributions improve
the local-first CLI, documentation, examples, tests, and failure messages.

Please keep the MVP boring and reliable:

- Prefer readable Markdown over hidden state.
- Prefer explicit files over magical behavior.
- Keep changes aligned with the local-first CLI and human-readable Markdown
  model.
- Update tests and docs with behavior changes.

## License

Apache-2.0. See [LICENSE](LICENSE).
