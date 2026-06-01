# Active Plan

## Objective

Build the first local-first Checkpoint CLI that proves the ContextOS cross-agent continuity loop.

## Build sequence

1. Verify package installation and CLI entry point.
2. Make `checkpoint init` create the repo memory structure safely.
3. Make `checkpoint setup-user` create `~/.contextos/about-me.md` from template.
4. Make `checkpoint status` summarize current project memory.
5. Make `checkpoint resume --for codex --task TASK-001` emit a useful context pack.
6. Make `checkpoint handoff` write durable handoff files and append events.
7. Add tests for init, status, resume, and handoff.
8. Leave a Codex handoff for the next agent.

## Current recommended agent

Codex.

## Why Codex

The next step is implementation of the local CLI scaffold, not further strategy.
