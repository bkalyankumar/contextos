@AGENTS.md

# Claude-specific guidance

Use Claude primarily for:

- architecture planning
- task decomposition
- critical reasoning
- design review
- strategy
- hard debugging handoffs

When resuming this project, inspect local ContextOS state first if it exists:

1. `.contextos/handoffs/latest.md`
2. `.contextos/tasks/active/`
3. `.contextos/plans/active-plan.md`
4. `docs/mvp-spec.md`
5. `docs/technical-architecture.md`

In a public clone, `.contextos/` may be absent because this repository keeps its
own agent handoffs and internal working plans local-only. In that case, start
from `README.md`, `docs/mvp-spec.md`, `docs/technical-architecture.md`, and
`docs/roadmap.md`.

If Codex or another agent hands work back, produce a short continuation plan and
update the relevant local task file before handing off again.

## Health Stack

- typecheck: mypy src
- lint: ruff check .
- test: pytest
- deadcode: vulture src tests
