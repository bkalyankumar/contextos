# Checkpoint MVP Spec

## Goal

Build a local-first CLI that makes AI coding work resumable and transferable across agents.

## Primary job

A developer should be able to:

1. plan in Claude,
2. import or write the plan into repo memory,
3. continue implementation in Codex,
4. hand off hard issues to Claude Code,
5. delegate long-running scoped work to Antigravity,
6. return to Claude later with full continuation context.

## MVP commands

```bash
checkpoint setup-user
checkpoint init
checkpoint status
checkpoint resume --for codex --task TASK-001
checkpoint handoff --from codex --to claude-code --task TASK-001
```

## MVP files

```text
~/.contextos/about-me.md

repo/
  AGENTS.md
  CLAUDE.md
  .contextos/
    context/
      project-summary.md
      architecture.md
      decisions.md
      constraints.md
      coding-standards.md
    plans/
      active-plan.md
    tasks/
      active/
      completed/
    handoffs/
      latest.md
    sessions/
      current.md
    state/
      events.jsonl
```

## Resume output ordering

`checkpoint resume` should emit:

1. current task and status
2. current blocker
3. non-negotiable constraints
4. relevant plan
5. relevant architecture
6. relevant files
7. recent handoff
8. next recommended action
9. handoff instructions

## Modes

```bash
checkpoint resume --for claude --mode planning
checkpoint resume --for codex --mode implement
checkpoint resume --for claude-code --mode debug
checkpoint resume --for antigravity --mode autonomous
```

## Initial success metric

A developer can open the repo, run:

```bash
checkpoint resume --for codex --task TASK-001
```

and get a context pack that is good enough to paste into Codex without re-explaining the product.

## Out of scope for MVP

- cloud sync
- team workspaces
- dashboards
- IDE extensions
- hosted agent runtime
- Tree-sitter indexing
- vector search
- enterprise policy engine
