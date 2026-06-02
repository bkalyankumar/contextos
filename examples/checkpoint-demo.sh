#!/usr/bin/env bash
set -euo pipefail

CHECKPOINT_BIN="${CHECKPOINT_BIN:-checkpoint}"
DEMO_ROOT="${1:-$(mktemp -d "${TMPDIR:-/tmp}/checkpoint-demo.XXXXXX")}"
DEMO_HOME="$DEMO_ROOT/home"
PROJECT_ROOT="$DEMO_ROOT/project"

if [[ "$CHECKPOINT_BIN" == */* ]]; then
  CHECKPOINT_DIR="$(cd "$(dirname "$CHECKPOINT_BIN")" && pwd)"
  CHECKPOINT_BIN="$CHECKPOINT_DIR/$(basename "$CHECKPOINT_BIN")"
fi

mkdir -p "$DEMO_HOME" "$PROJECT_ROOT"
export HOME="$DEMO_HOME"

cd "$PROJECT_ROOT"

"$CHECKPOINT_BIN" setup-user
"$CHECKPOINT_BIN" init

cat > .contextos/context/project-summary.md <<'MARKDOWN'
# Project Summary

Tiny Notes is a small demo app. The next agent should add one visible feature
without changing the project shape.
MARKDOWN

cat > .contextos/context/constraints.md <<'MARKDOWN'
# Constraints

- Keep the change local.
- Do not add dependencies.
- Leave a clear handoff before stopping.
MARKDOWN

cat > .contextos/context/architecture.md <<'MARKDOWN'
# Architecture

The demo has one CLI entry point and one Markdown-backed task list. There is no
server, database, or hosted service.
MARKDOWN

cat > .contextos/context/decisions.md <<'MARKDOWN'
# Decisions

## DEC-001: Keep the first feature tiny

Reason: the next agent should prove it can continue the task before expanding
scope.

Decision: add one visible improvement, run checks, and leave a handoff.
MARKDOWN

cat > .contextos/plans/active-plan.md <<'MARKDOWN'
# Active Plan

1. Read the active task.
2. Make one small visible change.
3. Run checks.
4. Leave a handoff for the next agent.
MARKDOWN

cat > .contextos/tasks/active/TASK-001.md <<'MARKDOWN'
# TASK-001: Add a tiny feature

## Goal

Add one small visible improvement to Tiny Notes.

## Relevant Files

- `README.md`

## Next Step

Inspect the repo, make the change, run checks, and update the handoff.
MARKDOWN

"$CHECKPOINT_BIN" status
"$CHECKPOINT_BIN" handoff \
  --from claude \
  --to codex \
  --task TASK-001 \
  --status in_progress \
  --summary "Planned the tiny feature; Codex should implement it."
"$CHECKPOINT_BIN" continue --from claude --for codex

printf '\nDemo project: %s\n' "$PROJECT_ROOT"
