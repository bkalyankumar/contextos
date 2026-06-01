# Contributing

Checkpoint is a local-first CLI for ContextOS. Keep contributions boring, explicit, and easy to verify.

## What To Work On

Good first contributions:

- clearer CLI errors and recovery messages
- tests for handoff, task, and continuation edge cases
- documentation and examples for real agent-switch workflows
- deterministic generated Markdown improvements
- redaction tests for generated continuation output

Please do not open large PRs for hosted sync, dashboards, IDE extensions,
Tree-sitter indexing, vector databases, or agent runtimes. Those are outside the
current MVP boundary.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

If you are offline and already have build dependencies installed, use:

```bash
python -m pip install --no-build-isolation -e '.[dev]'
```

## Verify

```bash
mypy src
ruff check .
pytest
vulture src tests
checkpoint --help
checkpoint status
checkpoint continue
```

## Contribution Rules

- Keep project state in readable Markdown files.
- Do not store secrets, tokens, private credentials, or raw API keys in handoffs.
- Prefer deterministic generated files.
- Do not add hosted sync, dashboards, vector databases, IDE extensions, or multi-agent runtimes to the MVP.
- Update docs and tests with behavior changes.
- Leave a ContextOS handoff when finishing a meaningful work session.

## Pull Requests

Before opening a PR:

- Keep the diff focused on one behavior or documentation improvement.
- Include tests for behavior changes.
- Update `CHANGELOG.md` when user-visible behavior changes.
- Update ContextOS handoff files for meaningful implementation sessions.
- Confirm no generated pack, handoff, log, or doc contains secrets.

## Security Reports

Do not file public issues for vulnerabilities. Follow `SECURITY.md`.
