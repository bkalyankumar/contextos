from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .continuation import (
    ContinuationError,
    append_continue_event,
    detect_agent_report,
    generate_continuation_pack,
    write_output_all_or_error,
)
from .store import (
    ProjectPaths,
    create_handoff,
    generate_resume_pack,
    init_project,
    init_user,
    list_active_tasks,
    read_text,
)

app = typer.Typer(no_args_is_help=True, help="Checkpoint CLI for local-first ContextOS continuity")
console = Console()


def require_existing_root(root: Path) -> Path:
    resolved = root.resolve()
    if not resolved.exists():
        console.print(f"Error: project root does not exist: {resolved}", markup=False)
        raise typer.Exit(1)
    if not resolved.is_dir():
        console.print(f"Error: project root is not a directory: {resolved}", markup=False)
        raise typer.Exit(1)
    return resolved


def print_raw(text: str) -> None:
    """Write Markdown exactly as stored/generated, without Rich markup parsing."""
    console.out(text.rstrip())


@app.command("setup-user")
def setup_user(
    overwrite: bool = typer.Option(False, help="Overwrite existing user files."),
) -> None:
    """Create user-level ContextOS files under ~/.contextos."""
    written = init_user(overwrite=overwrite)
    if written:
        console.print("Created user context files:", markup=False)
        for path in written:
            console.print(f"- {path}", markup=False)
    else:
        console.print("User context already exists. Use --overwrite to replace templates.", markup=False)


@app.command("init")
def init(
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
    overwrite: bool = typer.Option(False, help="Overwrite existing project files."),
) -> None:
    """Initialize project-level ContextOS files."""
    root = root.resolve()
    written = init_project(root=root, overwrite=overwrite)
    console.print(f"Initialized ContextOS project at {root}", markup=False)
    if written:
        console.print("Created files:", markup=False)
        for path in written:
            console.print(f"- {path.relative_to(root)}", markup=False)
    else:
        console.print("No files overwritten. Existing files were preserved.", markup=False)


@app.command("status")
def status(
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Show current ContextOS project status."""
    root = require_existing_root(root)
    paths = ProjectPaths(root=root)
    table = Table(title="ContextOS Status")
    table.add_column("Item")
    table.add_column("Status")

    table.add_row("Project root", str(root))
    table.add_row(".contextos", "yes" if paths.contextos.exists() else "missing")
    table.add_row("AGENTS.md", "yes" if (root / "AGENTS.md").exists() else "missing")
    table.add_row("CLAUDE.md", "yes" if (root / "CLAUDE.md").exists() else "missing")
    table.add_row("Latest handoff", "yes" if paths.latest_handoff.exists() else "missing")
    table.add_row("Active tasks", str(len(list_active_tasks(paths))))
    console.print(table)

    tasks = list_active_tasks(paths)
    if tasks:
        console.print("\nActive tasks:", markup=False)
        for task in tasks:
            console.print(f"- {task.relative_to(root)}", markup=False)


@app.command("resume")
def resume(
    target_agent: str = typer.Option("codex", "--for", help="Target agent: codex, claude, claude-code, antigravity."),
    mode: str = typer.Option("implement", help="Mode: planning, implement, debug, autonomous."),
    task: str | None = typer.Option(None, help="Task id or filename fragment."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Optional file to write the resume pack."),
) -> None:
    """Generate an ordered context pack for an agent."""
    paths = ProjectPaths(root=root.resolve())
    pack = generate_resume_pack(paths, target_agent=target_agent, mode=mode, task_id=task)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(pack, encoding="utf-8")
        console.print(f"Wrote resume pack to {output}", markup=False)
    else:
        print_raw(pack)


@app.command("continue")
def continue_command(
    source_agent: str | None = typer.Option(None, "--from", help="Source agent handoff to continue from."),
    target_agent: str | None = typer.Option(None, "--for", help="Target agent. Defaults to detected current agent."),
    task: str | None = typer.Option(None, help="Task id or filename fragment."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Optional file to write the continuation pack."),
) -> None:
    """Continue from the latest ContextOS state with inferred source, target, and task."""
    paths = ProjectPaths(root=root.resolve())
    try:
        pack, context = generate_continuation_pack(
            paths,
            source_agent=source_agent,
            target_agent=target_agent,
            task_id=task,
        )
        if output:
            write_output_all_or_error(output, pack)
            append_continue_event(context, output=output)
            console.print(f"Wrote continuation pack to {output}", markup=False)
        else:
            append_continue_event(context, output=None)
            print_raw(pack)
    except ContinuationError as exc:
        console.print(f"Error: {exc}", markup=False)
        console.print(exc.recovery, markup=False)
        raise typer.Exit(1) from exc


@app.command("detect-agent")
def detect_agent(
    target_agent: str | None = typer.Option(None, "--for", help="Override target agent for diagnostics."),
) -> None:
    """Print conservative current-agent detection diagnostics."""
    print_raw(detect_agent_report(target_agent))


@app.command("handoff")
def handoff(
    from_agent: str = typer.Option(..., "--from", help="Agent handing off work."),
    to_agent: str = typer.Option("codex", "--to", help="Next recommended agent."),
    task: str = typer.Option("TASK-001", "--task", help="Task id."),
    status_value: str = typer.Option("in_progress", "--status", help="Task status."),
    summary: str = typer.Option("", help="Summary of work completed."),
    files: str = typer.Option("", help="Comma-separated files changed."),
    tests: str = typer.Option("", help="Tests run and results."),
    blockers: str = typer.Option("", help="Current blockers."),
    decisions: str = typer.Option("", help="Durable decisions made."),
    continuation: str = typer.Option("", help="Continuation prompt for next agent."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Create a durable handoff and update latest.md."""
    paths = ProjectPaths(root=root.resolve())
    target = create_handoff(
        paths,
        from_agent=from_agent,
        to_agent=to_agent,
        task_id=task,
        status=status_value,
        summary=summary,
        files_changed=[item.strip() for item in files.split(",") if item.strip()],
        tests_run=tests,
        blockers=blockers,
        decisions=decisions,
        continuation_prompt=continuation,
    )
    console.print(f"Created handoff: {target.relative_to(root.resolve())}", markup=False)
    console.print(f"Updated latest handoff: {paths.latest_handoff.relative_to(root.resolve())}", markup=False)


@app.command("show")
def show(
    path: Path = typer.Argument(..., help="Context file path to print."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Print a context file from the repo."""
    root = require_existing_root(root)
    full_path = path if path.is_absolute() else root / path
    if not full_path.exists():
        console.print(f"Error: file not found: {full_path}", markup=False)
        raise typer.Exit(1)
    if not full_path.is_file():
        console.print(f"Error: path is not a file: {full_path}", markup=False)
        raise typer.Exit(1)
    print_raw(read_text(full_path))
