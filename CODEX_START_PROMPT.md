You are taking over implementation of the ContextOS / Checkpoint MVP from a strategic planning session.

First read these files in order:

1. `AGENTS.md`
2. `.contextos/handoffs/latest.md`
3. `.contextos/plans/active-plan.md`
4. `checkpoint status`
5. `docs/mvp-spec.md`
6. `docs/technical-architecture.md`
7. `docs/business-plan.md`

Your immediate goal is to turn this starter into a usable local-first CLI.

Start with TASK-001:

- verify the package installs with `pip install -e '.[dev]'`
- run `checkpoint --help`, `checkpoint status`, and `checkpoint resume --for codex --task TASK-001`
- improve the CLI only where needed to make the local workflow reliable
- add or fix tests for the core commands
- keep the MVP simple and Markdown-first

Do not build hosted sync, dashboards, IDE extensions, vector search, Tree-sitter indexing, MCP, or agent orchestration yet.

Definition of done for this Codex session:

1. CLI commands work locally.
2. Tests pass.
3. `checkpoint resume --for codex --task TASK-001` emits a useful context pack.
4. `checkpoint handoff --from codex --to claude-code --task TASK-001 --status in_progress` writes a durable handoff.
5. You update the relevant task file and `.contextos/handoffs/latest.md` before ending.

If you create or resume a task, keep it under `.contextos/tasks/active/` while it is in progress and move it to `.contextos/tasks/completed/` when done.

At the end, leave a handoff with:

- what changed
- files modified
- tests run
- blockers
- decisions
- next recommended agent
- exact continuation prompt
