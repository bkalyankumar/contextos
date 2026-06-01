# Architecture

## Core model

ContextOS uses canonical repo memory plus agent-specific projections.

```text
Canonical ContextOS State
  -> Codex context pack
  -> Claude Code debug pack
  -> Claude planning pack
  -> Antigravity autonomous pack
```

## Memory levels

### User-level memory

```text
~/.contextos/about-me.md
```

Personal workflow and preferences. Local/private by default.

### Project-level memory

```text
repo/.contextos/
```

Repo-specific context, plans, tasks, decisions, and handoffs.

### Projection files

```text
AGENTS.md
CLAUDE.md
```

Compatibility files read by existing agents.

## Initial implementation

Use Markdown files as the source of truth. The CLI reads the files, assembles ordered context packs, and writes handoffs.

Do not start with hosted sync, vector search, Tree-sitter, or dashboards.
