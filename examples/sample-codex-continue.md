# Example Codex Continue Flow

Run the reusable tiny demo from this repository:

```bash
bash examples/checkpoint-demo.sh
```

When running from a source checkout before installing the console script:

```bash
CHECKPOINT_BIN=.venv/bin/checkpoint bash examples/checkpoint-demo.sh
```

Expected result:

- `checkpoint setup-user` creates user-level context in an isolated demo home
- `checkpoint init` creates local `.contextos/` project memory
- the demo seeds meaningful project summary, constraints, architecture, and task files
- `checkpoint handoff` records a Claude-to-Codex handoff
- `checkpoint continue --from claude --for codex` prints a Codex continuation pack

The key output sections are:

- Continuation provenance
- Target agent
- Current task and status
- Recent handoff
- Project summary
- Handoff instructions
