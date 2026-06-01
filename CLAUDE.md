@AGENTS.md

# Claude-specific guidance

Use Claude primarily for:

- architecture planning
- task decomposition
- critical reasoning
- design review
- strategy
- hard debugging handoffs

When resuming this project, first inspect:

1. `.contextos/handoffs/latest.md`
2. `.contextos/tasks/active/`
3. `.contextos/plans/active-plan.md`
4. `docs/mvp-spec.md`
5. `docs/technical-architecture.md`

If Codex or another agent hands work back, produce a short continuation plan and update the relevant task file before handing off again.

## Health Stack

- typecheck: mypy src
- lint: ruff check .
- test: pytest
- deadcode: vulture src tests
