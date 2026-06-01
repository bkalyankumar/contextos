# ContextOS Business Plan

## One-line description

ContextOS is a shared engineering memory and handoff layer for multi-agent software development.

Checkpoint is the CLI that automatically keeps Claude, Codex, Claude Code, Antigravity, Cursor, Windsurf, and future agents synchronized around the same repo, plan, task state, and handoff history.

## Category

Repo-native continuity infrastructure for AI-assisted software engineering.

Avoid generic positioning such as:

- AI memory app
- coding assistant
- chatbot memory
- agent runtime

Own the more precise problem:

```text
AI engineering continuity is fragmented across tools, sessions, models, machines, and repos.
```

## Core wedge

Automatic handoff between AI coding agents.

```text
Plan in Claude -> Code in Codex -> Debug in Claude Code -> Delegate to Antigravity -> Resume anywhere
```

## Target early adopters

1. AI-native developers using 2+ coding agents.
2. Claude + Codex power users.
3. Cursor/Windsurf users who also use terminal agents.
4. Solo founders and indie hackers building with AI agents.
5. Developers working in medium-sized repos where context reconstruction is painful.
6. Agentic workflow builders who need durable state across tools.

## Pain

Developers repeatedly reconstruct:

- repo architecture
- current plan
- task status
- decisions
- constraints
- debugging context
- test results
- handoff state

Tool-native memories help, but they are usually product-shaped and weaker when switching tools.

## Product promise

```text
Your AI engineering context follows the work, not the tool.
```

## Open-source strategy

Open-source the local habit loop:

- Checkpoint CLI
- repo memory schema
- `.contextos/` structure
- local handoffs
- local resume packs
- generated `AGENTS.md` / `CLAUDE.md`
- basic adapters
- local encrypted export/import
- local MCP server eventually

Reason:

The open-source layer should become the standard repo-native continuity format for AI engineering.

## Paid strategy

Monetize where local-only breaks:

1. Encrypted cross-machine Context Vault.
2. Pro automation and background sync.
3. Team memory and shared project context.
4. Enterprise governance, audit, policy, SSO, self-hosting, BYOK, data residency.

## Pricing hypothesis

Free / open source:

- local CLI
- local resume
- local handoffs
- local schema
- local agent projections

Pro:

- $10-$20/month
- encrypted multi-machine sync
- device pairing
- backup/restore
- snapshot history
- background handoff automation

Team:

- $15-$30/user/month
- shared team memory
- shared project contexts
- team handoff history
- GitHub/GitLab integration
- Slack/Teams notifications
- role-based access

Enterprise:

- custom annual contract
- self-hosted vault
- SSO/SCIM
- audit logs
- retention controls
- policy engine
- BYOK
- compliance reporting

## Long-term moat

1. The `.contextos/` schema becomes a de facto standard.
2. Developers build the daily habit of `checkpoint resume` and `checkpoint handoff`.
3. Project memory compounds across plans, tasks, decisions, and handoffs.
4. Tool adapters become reliable and trusted.
5. Team/enterprise context graphs become operationally important.
6. Privacy-first sync and governance become hard to replicate.

## Go-to-market

Phase 1: Developer open-source launch.

- Launch with a crisp demo: Claude -> Codex -> Claude Code -> Antigravity -> Claude.
- Publish examples for real repos.
- Make `checkpoint resume --for codex` immediately useful.

Phase 2: Pro sync.

- Sell encrypted multi-machine continuity to power users.
- Focus on not losing context when switching machines.

Phase 3: Team memory.

- Sell shared AI engineering context to small teams.
- Focus on onboarding, handoffs, and consistent agent instructions.

Phase 4: Enterprise governance.

- Sell control, privacy, auditability, and policy for AI-assisted engineering.
