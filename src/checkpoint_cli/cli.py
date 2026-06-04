from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .continuation import (
    ContinuationError,
    append_continue_event,
    detect_agent_report,
    detect_current_agent,
    generate_continuation_pack,
    write_output_all_or_error,
)
from .runtime import (
    build_repo_map,
    classify_steer_message,
    create_execution_contract,
    doctor_report,
    finalize_execution,
    guard_report,
    history_records,
    json_output,
    latest_task_id,
    mcp_server,
    memory_records,
    query_repo_map,
    render_continuity_view,
    repo_map_status,
    search_memory,
)
from .store import (
    ProjectPaths,
    StoreFilesystemError,
    create_handoff,
    generate_resume_pack,
    init_project,
    init_user,
    list_active_tasks,
    read_text,
    safe_write,
)

app = typer.Typer(no_args_is_help=True, help="Checkpoint CLI for local-first ContextOS continuity")
map_app = typer.Typer(help="Build and query the local ContextOS RepoMap.")
memory_app = typer.Typer(help="Inspect local failure, strategy, and area memory.")
app.add_typer(map_app, name="map")
app.add_typer(memory_app, name="memory")
console = Console()


def print_filesystem_error(exc: StoreFilesystemError) -> None:
    console.print(f"Error: {exc}", markup=False)
    console.print(exc.recovery, markup=False)


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


def relative_receipt_path(path: Path | str | None, root: Path) -> str:
    if not path:
        return "not found"
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(root.resolve()))
    except ValueError:
        return str(resolved)


@app.command("setup-user")
def setup_user(
    overwrite: bool = typer.Option(False, help="Overwrite existing user files."),
) -> None:
    """Create user-level ContextOS files under ~/.contextos."""
    try:
        written = init_user(overwrite=overwrite)
    except StoreFilesystemError as exc:
        print_filesystem_error(exc)
        raise typer.Exit(1) from exc
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
    try:
        written = init_project(root=root, overwrite=overwrite)
    except StoreFilesystemError as exc:
        print_filesystem_error(exc)
        raise typer.Exit(1) from exc
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
    create_execution_contract(paths, target_agent=target_agent, task_id=task)
    if output:
        try:
            safe_write(output, pack, overwrite=True)
        except StoreFilesystemError as exc:
            print_filesystem_error(exc)
            raise typer.Exit(1) from exc
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
    try:
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
    except StoreFilesystemError as exc:
        print_filesystem_error(exc)
        raise typer.Exit(1) from exc
    console.print(f"Created handoff: {target.relative_to(root.resolve())}", markup=False)
    console.print(f"Updated latest handoff: {paths.latest_handoff.relative_to(root.resolve())}", markup=False)


@app.command("finalize")
def finalize(
    summary_arg: str = typer.Argument("", help="Optional closeout summary."),
    from_agent: str | None = typer.Option(None, "--from", help="Agent finalizing the work. Defaults to detected agent."),
    to_agent: str = typer.Option("codex", "--to", help="Next recommended agent."),
    task: str | None = typer.Option(None, "--task", help="Task id. Defaults to latest contract or sole active task."),
    status_value: str = typer.Option("success", "--status", help="Final status: success, failure, blocked, etc."),
    summary: str = typer.Option("", "--summary", help="Summary of what happened. Overrides the positional summary."),
    files: str = typer.Option("", "--files", "--changed", help="Comma-separated files changed."),
    tests: str = typer.Option("", "--tests", "--test", help="Tests or validation run."),
    blockers: str = typer.Option("", help="Remaining blockers."),
    decisions: str = typer.Option("", help="Durable decisions made."),
    next_action: str = typer.Option("", "--next-action", "--next", help="Exact continuation prompt / next action."),
    failure_command: str = typer.Option("", help="Failed command to record in failure memory."),
    failure_exit_code: str = typer.Option("", help="Exit code for the failed command."),
    failure_message: str = typer.Option("", help="Failure message or error summary."),
    failure_file: str = typer.Option("", help="File related to the failure."),
    failure_phase: str = typer.Option("", help="Failure phase, e.g. test, build, install."),
    failure_status: str = typer.Option("observed", help="Failure status: observed, resolved, avoided."),
    failure_resolution: str = typer.Option("", help="Resolution or note for the failure."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Finalize work and update handoff, task state, execution summary, and continuity memory."""
    paths = ProjectPaths(root=root.resolve())
    resolved_from_agent = from_agent or detect_current_agent().agent
    resolved_task = task or latest_task_id(paths)
    resolved_summary = summary or summary_arg
    if not resolved_task:
        console.print("Error: no task could be inferred for finalize.", markup=False)
        active_tasks = list_active_tasks(paths)
        if active_tasks:
            console.print("Active task candidates:", markup=False)
            for active_task in active_tasks:
                console.print(f"- --task {active_task.stem} ({active_task.name})", markup=False)
        console.print("Pass `--task <TASK-ID>` or keep exactly one active task.", markup=False)
        raise typer.Exit(1)
    try:
        result = finalize_execution(
            paths,
            from_agent=resolved_from_agent,
            to_agent=to_agent,
            task_id=resolved_task,
            status=status_value,
            summary=resolved_summary,
            files=files,
            tests=tests,
            blockers=blockers,
            decisions=decisions,
            next_action=next_action,
            failure_command=failure_command,
            failure_exit_code=failure_exit_code,
            failure_message=failure_message,
            failure_file=failure_file,
            failure_phase=failure_phase,
            failure_status=failure_status,
            failure_resolution=failure_resolution,
        )
    except StoreFilesystemError as exc:
        print_filesystem_error(exc)
        raise typer.Exit(1) from exc
    memory_counts = result["memory_counts"]
    console.print(f"Finalized task: {resolved_task}", markup=False)
    console.print(f"Finalized from: {resolved_from_agent}", markup=False)
    console.print(f"Updated handoff: {relative_receipt_path(result['handoff_path'], root)}", markup=False)
    console.print(f"Updated latest handoff: {relative_receipt_path(result['latest_handoff_path'], root)}", markup=False)
    console.print(f"Updated task state: {relative_receipt_path(result['task_path'], root)}", markup=False)
    console.print(f"Updated execution summary: {relative_receipt_path(result['execution_summary_path'], root)}", markup=False)
    console.print(f"Contract compliance: {result['contract_compliance']['status']}", markup=False)
    console.print(
        "Memory records: "
        f"{memory_counts['failures']} failures, "
        f"{memory_counts['strategies']} strategies, "
        f"{memory_counts['areas']} areas",
        markup=False,
    )
    if result["failure"]:
        console.print("Recorded failure memory.", markup=False)
    if result["strategy"]:
        console.print("Recorded strategy memory.", markup=False)


@app.command("history")
def history(
    limit: int = typer.Option(20, "--limit", help="Maximum events to show."),
    event_type: str | None = typer.Option(None, "--type", help="Filter by event type."),
    json_flag: bool = typer.Option(False, "--json", help="Print machine-readable history."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Show recent ContextOS events from the local event log."""
    result = history_records(ProjectPaths(root=root.resolve()), limit=limit, event_type=event_type)
    if json_flag:
        print_raw(json_output(result))
        return
    table = Table(title="ContextOS History")
    table.add_column("Created")
    table.add_column("Type")
    table.add_column("Task")
    table.add_column("Status")
    for event in result["events"]:
        table.add_row(
            str(event.get("created_at", "")),
            str(event.get("type", "")),
            str(event.get("task_id", "")),
            str(event.get("status", event.get("outcome", ""))),
        )
    console.print(table)


@app.command("view")
def view(
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Generate a local Markdown and Mermaid continuity view."""
    paths = ProjectPaths(root=root.resolve())
    try:
        result = render_continuity_view(paths)
    except StoreFilesystemError as exc:
        print_filesystem_error(exc)
        raise typer.Exit(1) from exc
    console.print(f"Wrote continuity view: {result['view'].relative_to(root.resolve())}", markup=False)
    console.print(f"Wrote continuity map: {result['map'].relative_to(root.resolve())}", markup=False)


@app.command("doctor")
def doctor(
    json_flag: bool = typer.Option(False, "--json", help="Print machine-readable diagnostics."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Inspect ContextOS continuity health."""
    report = doctor_report(ProjectPaths(root=root.resolve()))
    if json_flag:
        print_raw(json_output(report))
        return
    table = Table(title="ContextOS Doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")
    for check in report["checks"]:
        table.add_row(check["name"], check["status"], check["detail"])
    console.print(table)
    if report["recommended_actions"]:
        console.print("\nRecommended actions:", markup=False)
        for action in report["recommended_actions"]:
            console.print(f"- {action}", markup=False)


@app.command("guard")
def guard(
    action: str = typer.Option("startup", "--action", help="startup, before_edit, scope_change, final_answer, finalize."),
    json_flag: bool = typer.Option(False, "--json", help="Print machine-readable guard output."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Run compact read-only continuity checks before a work boundary."""
    report = guard_report(ProjectPaths(root=root.resolve()), action=action)
    if json_flag:
        print_raw(json_output(report))
        return
    console.print(f"Severity: {report['severity']}", markup=False)
    console.print(report["message"], markup=False)
    for warning in report["warnings"]:
        console.print(f"- {warning['name']}: {warning['detail']}", markup=False)


@app.command("steer")
def steer(
    message: str = typer.Option(..., "--message", help="User message or interruption to classify."),
    current_action: str = typer.Option("", "--current-action", help="What the agent is currently doing."),
    json_flag: bool = typer.Option(False, "--json", help="Print machine-readable classification."),
) -> None:
    """Classify a user interruption during active work."""
    report = classify_steer_message(message, current_action)
    if json_flag:
        print_raw(json_output(report))
        return
    console.print(f"Classification: {report['classification']}", markup=False)
    console.print(report["recommended_response"], markup=False)


@memory_app.command("list")
def memory_list(
    kind: str = typer.Option("all", "--kind", help="all, failures, strategies, or areas."),
    limit: int = typer.Option(20, "--limit", help="Maximum records per kind."),
    json_flag: bool = typer.Option(False, "--json", help="Print machine-readable memory."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """List local continuity memory records."""
    result = memory_records(ProjectPaths(root=root.resolve()), kind=kind, limit=limit)
    if json_flag:
        print_raw(json_output(result))
        return
    if "failures" in result:
        console.print("Failures:", markup=False)
        for row in result["failures"]:
            console.print(f"- {row.get('created_at', '')} {row.get('status', '')}: {row.get('message', '')}", markup=False)
    if "strategies" in result:
        console.print("Strategies:", markup=False)
        for row in result["strategies"]:
            console.print(f"- {row.get('created_at', '')} {row.get('task_type', '')}: {row.get('summary', '')}", markup=False)
    if "areas" in result:
        console.print("Areas:", markup=False)
        areas = result["areas"].get("areas", {}) if isinstance(result["areas"], dict) else {}
        for area, counts in areas.items():
            console.print(f"- {area}: {counts}", markup=False)


@memory_app.command("search")
def memory_search(
    query: str = typer.Argument(..., help="Search query."),
    kind: str = typer.Option("all", "--kind", help="all, failures, or strategies."),
    limit: int = typer.Option(20, "--limit", help="Maximum matches."),
    json_flag: bool = typer.Option(False, "--json", help="Print machine-readable matches."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Search local failure and strategy memory."""
    result = search_memory(ProjectPaths(root=root.resolve()), query=query, kind=kind, limit=limit)
    if json_flag:
        print_raw(json_output(result))
        return
    if not result["matches"]:
        console.print(f"No memory matches for: {query}", markup=False)
        return
    for match in result["matches"]:
        record = match["record"]
        label = record.get("message") or record.get("summary") or record.get("task_id", "")
        console.print(f"{match['kind']} score={match['score']}: {label}", markup=False)


@app.command("mcp-server")
def mcp_server_command(
    profile: str = typer.Option("readonly", "--profile", help="readonly or full."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Run the optional local MCP server over ContextOS continuity state."""
    normalized = "full" if profile == "full" else "readonly"
    raise typer.Exit(mcp_server(ProjectPaths(root=root.resolve()), profile=normalized))


@map_app.command("refresh")
def map_refresh(
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Refresh the stdlib RepoMap index."""
    try:
        status = build_repo_map(ProjectPaths(root=root.resolve()))
    except StoreFilesystemError as exc:
        print_filesystem_error(exc)
        raise typer.Exit(1) from exc
    console.print(f"RepoMap refreshed: {status['files_indexed']} files, {status['symbols_indexed']} symbols", markup=False)


@map_app.command("status")
def map_status(
    json_flag: bool = typer.Option(False, "--json", help="Print machine-readable RepoMap status."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Show local RepoMap status."""
    status = repo_map_status(ProjectPaths(root=root.resolve()))
    if json_flag:
        print_raw(json_output(status))
        return
    table = Table(title="ContextOS RepoMap")
    table.add_column("Item")
    table.add_column("Status")
    for key in ["status", "provider_available", "index_available", "query_available", "refresh_available", "files_indexed", "symbols_indexed"]:
        table.add_row(key, str(status.get(key, "unknown")))
    console.print(table)


@map_app.command("query")
def map_query(
    query: str = typer.Argument(..., help="Search query."),
    limit: int = typer.Option(5, "--limit", help="Maximum matches."),
    json_flag: bool = typer.Option(False, "--json", help="Print machine-readable matches."),
    root: Path = typer.Option(Path.cwd(), "--root", help="Repository root."),
) -> None:
    """Query the local RepoMap index."""
    result = query_repo_map(ProjectPaths(root=root.resolve()), query, limit=limit)
    if json_flag:
        print_raw(json_output(result))
        return
    if not result["matches"]:
        console.print(f"No RepoMap matches for: {query}", markup=False)
        return
    for match in result["matches"]:
        console.print(f"{match['path']} (score {match['score']})", markup=False)


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
