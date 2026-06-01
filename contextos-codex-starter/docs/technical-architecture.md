# Technical Architecture

## MVP architecture

```text
Local Markdown Store
  -> Projection Engine
  -> Resume Context Pack
  -> Agent-specific Handoff
```

## Components

### 1. User memory

Location:

```text
~/.contextos/about-me.md
```

Contains personal workflow preferences and safety preferences.

### 2. Project memory

Location:

```text
repo/.contextos/
```

Contains project-level architecture, constraints, plans, tasks, and handoffs.

### 3. Projection files

Location:

```text
repo/AGENTS.md
repo/CLAUDE.md
```

Purpose:

- make Codex, Cursor, OpenHands, Windsurf, and other AGENTS-compatible tools read ContextOS guidance
- make Claude Code read ContextOS guidance through `CLAUDE.md`

### 4. Event log

Location:

```text
.contextos/state/events.jsonl
```

Purpose:

- append-only operation history
- future sync/reconciliation
- recoverable handoff history

### 5. Future local index

Future location:

```text
.contextos/state/index.sqlite
```

Purpose:

- file summaries
- task mappings
- symbols
- dependency graph
- retrieval metadata

Do not build this until the Markdown-first workflow is validated.

## Future architecture

After MVP:

- Tree-sitter for AST extraction
- SQLite for canonical local state
- sqlite-vec or LanceDB behind interface for local vector retrieval
- NetworkX for local dependency graph
- watchfiles for incremental sync
- local MCP server for agent access
- encrypted Context Vault for remote sync

## Privacy model

Default:

- local-first
- no cloud required
- human-readable project memory
- secrets never stored
- encrypted export/import before hosted sync

Future paid sync:

- end-to-end encrypted vault
- device pairing
- offline-first local replica
- append-only event sync
- conflict-safe merge
