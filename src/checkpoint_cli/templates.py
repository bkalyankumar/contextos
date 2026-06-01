from __future__ import annotations

PROJECT_CONTEXT_FILES: dict[str, str] = {
    "project-summary.md": "# Project Summary\n\nDescribe what this project is and what the current product promise is.\n",
    "architecture.md": "# Architecture\n\nDescribe the key components, boundaries, data flow, and constraints.\n",
    "decisions.md": "# Decisions\n\nRecord durable engineering/product decisions here.\n",
    "constraints.md": "# Constraints\n\nList non-negotiable constraints agents must respect.\n",
    "coding-standards.md": "# Coding Standards\n\nList project coding conventions, test commands, and safety rules.\n",
}

USER_ABOUT_ME = """# about-me.md

## Preferred AI workflow

- Use Claude for architecture, planning, and critical reasoning.
- Use Codex for implementation.
- Use Claude Code for hard debugging and refactor review.
- Use Antigravity for long-running autonomous work with strict scope.

## Handoff preference

Every agent must leave a handoff with:

- what changed
- files touched
- tests run
- blockers
- decisions made
- next recommended agent
- exact continuation prompt

## Safety preferences

- Do not store secrets or credentials in context files.
- Ask before destructive actions.
- Keep MVPs simple and local-first.
"""

AGENTS_MD = """# AGENTS.md - ContextOS Project Instructions

This repository uses ContextOS-style persistent engineering memory.

## Always read before work

1. `.contextos/handoffs/latest.md`
2. `.contextos/plans/active-plan.md`
3. `.contextos/context/project-summary.md`
4. `.contextos/context/architecture.md`
5. `.contextos/context/constraints.md`
6. Relevant task file under `.contextos/tasks/active/`

## Always update before stopping

- `.contextos/handoffs/latest.md`
- the active task file under `.contextos/tasks/active/`
- `.contextos/context/decisions.md` if a durable decision was made

## Handoff requirement

Every handoff must include current task, status, files changed, tests run, blockers, decisions, next recommended agent, and continuation prompt.
"""

CLAUDE_MD = """@AGENTS.md

# Claude-specific guidance

Use Claude for architecture, planning, task decomposition, design review, and critical reasoning.

When resuming, inspect `.contextos/handoffs/latest.md` and `.contextos/tasks/active/` first.
"""
