"""
Local session usage ledger.

Public API: :func:`usage_root`, :func:`record_usage`, :func:`render_report`,
:func:`prune_usage`, and :func:`load_usage_runs`.

Side effects: writes and deletes files under ``.toolwright/usage`` only when the
caller invokes the corresponding command.
"""
from __future__ import annotations
from .usage_strings import (
    TEXT_SIGKILL,
    TEXT_KILLPG,
    TEXT_CURRENT_DIR,
    TEXT_INVALID_RUN_ID,
    TEXT_PARENT_DIR,
    TEXT_USAGE_META_GLOB,
    TEXT_VERIFICATION_TIMEOUT,
    TEXT_WRITE_READ_MODE,
    TEXT_VERIFICATION_EXIT_LINE,
    TEXT_USAGE_EXISTS,
    TEXT_TIMEOUT_AFTER,
    KEY_RUN_EXIT,
    EMPTY_STRING,
    KEY_AGENT,
    KEY_ARM,
    KEY_COMMIT,
    KEY_COST,
    KEY_ENTRIES,
    KEY_INPUT,
    KEY_MODEL,
    KEY_OUTPUT,
    KEY_REASONING,
    KEY_REWORK,
    KEY_RUN_ID,
    KEY_RUNS,
    KEY_TASK,
    KEY_TASK_ID,
    KEY_TOTAL,
    KEY_SESSION,
    KEY_USAGE_DIR,
    KEY_VERIFICATION_EXIT,
    KEY_VERIFIED,
    KEY_WORKING_DIRECTORY,
    TEXT_CANNOT_USE_BOTH,
    TEXT_COMMAND_NOT_FOUND,
    TEXT_NEED_SESSION_OR_COMMAND,
    TEXT_SESSION_NOT_FOUND,
    TEXT_SESSION_INVALID,
    TEXT_WINDOWS_OS,
    TEXT_PRUNE_YES_REQUIRED,
    TEXT_REPORT_HEADER,
    TEXT_REPORT_RULE,
    TEXT_REPORT_ROW,
    TEXT_USAGE_DIR_MISSING,
)

import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import BASH, EMPTY_STRING, KEY_WALL_TIME_SECONDS, NEWLINE, TEXT_META_JSON
from .paths import ToolWrightError
from .stats import RunSummary, load_runs
from .pilot_strings import TEXT_LC, TEXT_VERIFICATION_LOG
from .stats_strings import ENCODING_UTF8, KEY_IGNORE, TEXT_SESSION_JSONL

TEXT_COMMAND_ERR = 'command.err'
SECONDS_PER_DAY = 86400
DEFAULT_TIMEOUT = 3600
TEXT_TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'


def usage_root(target: Path) -> Path:
    """
    Return the usage ledger directory for a project.

    Parameters:
        target: project root.

    Returns:
        ``<target>/.toolwright/usage``.
    """
    return target / KEY_USAGE_DIR


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime(TEXT_TIMESTAMP_FORMAT)


def _validate_session(path: Path) -> None:
    events = 0
    for line in path.read_text(encoding=ENCODING_UTF8, errors=KEY_IGNORE).splitlines():
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError:
            continue
        events += 1
    if events == 0:
        raise ToolWrightError(TEXT_SESSION_INVALID.format(path))


def _verification(target: Path, command: str, timeout: int) -> tuple[int, str]:
    try:
        invocation = command if os.name == TEXT_WINDOWS_OS else [BASH, TEXT_LC, command]
        result = subprocess.run(
            invocation,
            cwd=str(target),
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            shell=os.name == TEXT_WINDOWS_OS,
        )
    except subprocess.TimeoutExpired:
        return 124, TEXT_VERIFICATION_TIMEOUT.format(timeout)
    return result.returncode, result.stdout + result.stderr


def _terminate_group(process: subprocess.Popen[str], signal_number: int) -> None:
    if hasattr(os, TEXT_KILLPG):
        try:
            os.killpg(process.pid, signal_number)
        except (ProcessLookupError, PermissionError):
            return
        return
    try:
        if signal_number == getattr(signal, TEXT_SIGKILL, signal.SIGTERM):
            process.kill()
        else:
            process.terminate()
    except ProcessLookupError:
        return


def _run_wrapper(command: list[str], target: Path, timeout: int) -> tuple[int, str, str, float]:
    started = time.monotonic()
    with tempfile.TemporaryFile(mode=TEXT_WRITE_READ_MODE, encoding=ENCODING_UTF8) as stdout_file:
        with tempfile.TemporaryFile(mode=TEXT_WRITE_READ_MODE, encoding=ENCODING_UTF8) as stderr_file:
            process = subprocess.Popen(
                command,
                cwd=str(target),
                stdout=stdout_file,
                stderr=stderr_file,
                text=True,
                start_new_session=True,
            )
            try:
                return_code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                _terminate_group(process, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    _terminate_group(process, getattr(signal, TEXT_SIGKILL, signal.SIGTERM))
                    process.wait()
                return_code = 124
            finally:
                _terminate_group(process, signal.SIGTERM)
            stdout_file.seek(0)
            stderr_file.seek(0)
            stdout = stdout_file.read()
            stderr = stderr_file.read()
    return return_code, stdout, stderr, time.monotonic() - started


def record_usage(
    target: Path,
    *,
    task: str,
    session: Path | None = None,
    command: list[str] | None = None,
    verify: str | None = None,
    agent: str = EMPTY_STRING,
    model: str = EMPTY_STRING,
    rework: int = 0,
    run_id: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """
    Record one session from a captured file or by running a wrapper command.

    Parameters:
        target: project root.
        task: task or label.
        session: existing session JSONL, when not running a command.
        command: command after ``--`` to execute and capture.
        verify: optional verification command.
        agent: agent label.
        model: model label.
        rework: rework cycles.
        run_id: optional directory name.
        timeout: wrapper timeout in seconds.

    Returns:
        The written metadata record.

    Side effects: writes ``meta.json`` and ``session.jsonl`` under
    ``.toolwright/usage/<run-id>`` and runs the wrapper and verification commands.
    """
    if bool(session) == bool(command):
        raise ToolWrightError(TEXT_CANNOT_USE_BOTH if session else TEXT_NEED_SESSION_OR_COMMAND)
    if session and not session.is_file():
        raise ToolWrightError(TEXT_SESSION_NOT_FOUND.format(session))
    identifier = run_id or _run_id()
    if identifier in (TEXT_CURRENT_DIR, TEXT_PARENT_DIR) or Path(identifier).name != identifier:
        raise ToolWrightError(TEXT_INVALID_RUN_ID.format(identifier))
    root = usage_root(target)
    destination = root / identifier
    if destination.exists():
        raise ToolWrightError(TEXT_USAGE_EXISTS.format(destination))
    destination.mkdir(parents=True)
    wall_seconds = 0.0
    run_exit = 0
    if command:
        try:
            run_exit, stdout, stderr, wall_seconds = _run_wrapper(command, target, timeout)
        except FileNotFoundError:
            shutil.rmtree(destination, ignore_errors=True)
            raise ToolWrightError(TEXT_COMMAND_NOT_FOUND.format(command[0]))
        (destination / TEXT_SESSION_JSONL).write_text(stdout, encoding=ENCODING_UTF8)
        (destination / TEXT_COMMAND_ERR).write_text(stderr, encoding=ENCODING_UTF8)
    else:
        shutil.copyfile(session, destination / TEXT_SESSION_JSONL)
    try:
        _validate_session(destination / TEXT_SESSION_JSONL)
    except ToolWrightError:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    verification_exit = -1
    verification_output = EMPTY_STRING
    if verify:
        verification_exit, verification_output = _verification(target, verify, timeout)
    meta = {
        KEY_RUN_ID: identifier,
        KEY_TASK_ID: task,
        KEY_ARM: KEY_SESSION,
        KEY_MODEL: model,
        KEY_AGENT: agent,
        KEY_WORKING_DIRECTORY: str(target),
        KEY_WALL_TIME_SECONDS: round(wall_seconds, 3),
        KEY_VERIFICATION_EXIT: verification_exit,
        KEY_REWORK: rework,
        KEY_RUN_EXIT: run_exit,
        KEY_COMMIT: EMPTY_STRING,
    }
    (destination / TEXT_META_JSON).write_text(json.dumps(meta, indent=2) + NEWLINE, encoding=ENCODING_UTF8)
    if verify:
        (destination / TEXT_VERIFICATION_LOG).write_text(TEXT_VERIFICATION_EXIT_LINE.format(verification_exit) + NEWLINE + verification_output, encoding=ENCODING_UTF8)
    return meta


def load_usage_runs(target: Path) -> list[RunSummary]:
    """
    Load recorded sessions through the existing stats reader.

    Parameters:
        target: project root.

    Returns:
        Run summaries, or an empty list when the ledger does not exist.
    """
    root = usage_root(target)
    if not root.is_dir():
        return []
    return load_runs([root])


def _meta_by_run(target: Path) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for meta_path in usage_root(target).glob(TEXT_USAGE_META_GLOB):
        try:
            meta = json.loads(meta_path.read_text(encoding=ENCODING_UTF8))
        except json.JSONDecodeError:
            continue
        values[str(meta.get(KEY_RUN_ID, meta_path.parent.name))] = meta
    return values


def _rework_by_run(target: Path) -> dict[str, int]:
    return {run_id: int(meta.get(KEY_REWORK, 0)) for run_id, meta in _meta_by_run(target).items()}


def _run_exit_by_run(target: Path) -> dict[str, int]:
    return {run_id: int(meta.get(KEY_RUN_EXIT, 0)) for run_id, meta in _meta_by_run(target).items()}


def render_report(target: Path) -> str:
    """
    Render a task-level Markdown report from the usage ledger.

    Parameters:
        target: project root.

    Returns:
        Markdown report text.

    Side effects: reads ``.toolwright/usage`` only.
    """
    runs = load_usage_runs(target)
    if not runs:
        return TEXT_USAGE_DIR_MISSING.format(usage_root(target)) + NEWLINE
    rework = _rework_by_run(target)
    run_exit = _run_exit_by_run(target)
    grouped: dict[tuple[str, str, str], list[RunSummary]] = {}
    for run in runs:
        grouped.setdefault((run.task_id, run.agent, run.model), []).append(run)
    lines = [TEXT_REPORT_HEADER, TEXT_REPORT_RULE]
    for task, agent, model in sorted(grouped):
        group = grouped[(task, agent, model)]
        verified = sum(
            1 for run in group
            if run.verification_exit == 0 and run_exit.get(run.run_id, 0) == 0
        )
        lines.append(
            TEXT_REPORT_ROW.format(
                task,
                agent,
                model,
                len(group),
                verified,
                sum(run.cost for run in group),
                sum(run.input_tokens for run in group),
                sum(run.output_tokens for run in group),
                sum(run.reasoning_tokens for run in group),
                sum(rework.get(run.run_id, 0) for run in group),
            )
        )
    return NEWLINE.join(lines) + NEWLINE


def report_payload(target: Path) -> dict[str, Any]:
    """
    Build a JSON-serializable task-level report.

    Parameters:
        target: project root.

    Returns:
        A mapping with one entry per task and a total.
    """
    runs = load_usage_runs(target)
    rework = _rework_by_run(target)
    run_exit = _run_exit_by_run(target)
    entries = []
    keys = sorted({(run.task_id, run.agent, run.model) for run in runs})
    for task, agent, model in keys:
        group = [run for run in runs if (run.task_id, run.agent, run.model) == (task, agent, model)]
        entries.append({
            KEY_TASK: task,
            KEY_AGENT: agent,
            KEY_MODEL: model,
            KEY_RUNS: len(group),
            KEY_VERIFIED: sum(
                1 for run in group
                if run.verification_exit == 0 and run_exit.get(run.run_id, 0) == 0
            ),
            KEY_COST: sum(run.cost for run in group),
            KEY_INPUT: sum(run.input_tokens for run in group),
            KEY_OUTPUT: sum(run.output_tokens for run in group),
            KEY_REASONING: sum(run.reasoning_tokens for run in group),
            KEY_REWORK: sum(rework.get(run.run_id, 0) for run in group),
        })
    return {KEY_ENTRIES: entries, KEY_TOTAL: len(runs)}


def prune_usage(target: Path, *, older_than_days: int, apply: bool, yes: bool) -> tuple[list[str], bool]:
    """
    Identify or delete usage entries older than a threshold.

    Parameters:
        target: project root.
        older_than_days: age threshold in days.
        apply: delete matching entries.
        yes: confirm deletion.

    Returns:
        Candidate run ids and whether deletion ran.

    Side effects: deletes directories only when ``apply`` and ``yes`` are true.
    """
    root = usage_root(target)
    if apply and not yes:
        raise ToolWrightError(TEXT_PRUNE_YES_REQUIRED)
    candidates = []
    if root.is_dir():
        cutoff = time.time() - older_than_days * SECONDS_PER_DAY
        for child in sorted(root.iterdir()):
            if child.is_dir() and child.stat().st_mtime < cutoff:
                candidates.append(child.name)
                if apply:
                    shutil.rmtree(child)
    return candidates, apply
