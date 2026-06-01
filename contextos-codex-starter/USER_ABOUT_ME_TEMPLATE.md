# about-me.md

## Identity

I am the owner/builder of ContextOS and Checkpoint.

## Preferred AI workflow

- Use Claude for architecture, planning, strategy, task decomposition, and critical reasoning.
- Use Codex for implementation and local CLI coding.
- Use Claude Code for complex debugging, refactor review, and failure analysis.
- Use Antigravity for long-running autonomous implementation with strict scope and stop conditions.

## Product preferences

- Brutally simple MVP first.
- Local-first and repo-native by default.
- Tool-agnostic over tool-specific lock-in.
- Markdown-readable state before complex databases.
- Compression over raw context dumping.

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

- Do not delete files outside the current repo.
- Ask before destructive actions.
- Do not store secrets or private credentials in context files.
- Do not introduce hosted/cloud dependencies into the MVP.
