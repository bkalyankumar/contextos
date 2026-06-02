# Changelog

All notable changes to Checkpoint are recorded here.

## Unreleased

## 0.1.1 - 2026-06-02

- Improved PyPI listing: clearer description, richer keywords, additional
  classifiers (license, OS, Python 3.13, version control topic), and
  Documentation URL.
- Added PyPI Trusted Publishing workflow and publishing instructions for the
  `checkpoint-cli` package.
- Documented `pip install checkpoint-cli` and `uv tool install checkpoint-cli`
  as the packaged install path.
- Refreshed public launch README positioning and source-install path.
- Added security policy, code of conduct, and public launch checklist.
- Added public package metadata to `pyproject.toml`.
- Added Apache-2.0 license.

## 0.1.0 - 2026-06-01

- Added the local-first Checkpoint CLI scaffold.
- Added `checkpoint setup-user`, `init`, `status`, `resume`, `continue`, `handoff`, `detect-agent`, and `show`.
- Added agent-specific context packs for Claude, Codex, Claude Code, Antigravity, and generic fallback.
- Added durable Markdown handoffs, append-only local events, and secret redaction for generated context.
- Deferred local encrypted export/import until the Markdown-first local loop is
  validated.

## Migration Notes

- No migrations are required for `0.1.0`.
- The project is still pre-release. Generated `.contextos/` files are Markdown and can be reviewed or edited directly.
