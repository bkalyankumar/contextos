# Contributing

Checkpoint is a local-first CLI for ContextOS. Keep contributions boring, explicit, and easy to verify.

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
pytest
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
