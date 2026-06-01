# Product Strategy

## Strategic conclusion

ContextOS should not compete as another AI coding assistant or generic memory product.

The opportunity is:

```text
Persistent engineering continuity is fragmented by tool, prompt surface, machine, and vendor runtime.
```

ContextOS should own the repo-native, tool-agnostic continuity layer.

## Product framing

ContextOS:

```text
Shared engineering context layer for multi-agent software development.
```

Checkpoint:

```text
CLI for creating, updating, and projecting shared context into the next AI coding tool.
```

## User-facing promise

```text
Plan in Claude. Code in Codex. Debug in Claude Code. Delegate to Antigravity. Resume anywhere.
```

## What ContextOS stores

- user profile and preferences
- project summary
- architecture
- constraints
- coding standards
- decisions
- plans
- task graph
- current progress
- handoff history
- test results
- blockers
- next recommended agent

## What ContextOS should not store by default

- raw full chat transcripts
- secrets
- API keys
- credentials
- production data
- customer PII
- large code dumps

## Core design principle

Agents should not hand context directly to each other.
Agents should read/write through ContextOS.

```text
Claude -> ContextOS -> Codex -> ContextOS -> Claude Code -> ContextOS -> Antigravity -> ContextOS -> Claude
```
