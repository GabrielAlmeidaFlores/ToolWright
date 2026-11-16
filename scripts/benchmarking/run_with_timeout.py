#!/usr/bin/env python3
"""
Run one command under a wall-clock limit and clean up its process group.

Public API: none. Execute as ``run_with_timeout.py SECONDS -- COMMAND [ARG...]``.

Side effects: starts ``COMMAND`` in a new process group, forwards ``SIGTERM`` to
the group when the limit expires, and terminates group members that survive the
command so benchmark MCP servers cannot outlive a run.

Returns the command exit status, ``124`` when the limit expires, or ``2`` for a
usage error.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.lib.python_strings import TEXT_MAIN

EXIT_USAGE = 2
EXIT_TIMEOUT = 124
ARGUMENT_SEPARATOR = '--'
POLL_SECONDS = 0.2
TERM_GRACE_SECONDS = 5.0
MINIMUM_ARGUMENTS = 4
SECONDS_INDEX = 1
SEPARATOR_INDEX = 2
COMMAND_START_INDEX = 3
USAGE = 'usage: run_with_timeout.py SECONDS -- COMMAND [ARG...]'


def signal_group(process_group: int, signal_number: int) -> None:
    """
    Send a signal to a process group, ignoring an already empty group.

    Parameters:
        process_group: group id, equal to the child pid when it starts a session.
        signal_number: signal to deliver.

    Returns:
        None.

    Side effects: delivers the signal to every live group member.
    """
    try:
        os.killpg(process_group, signal_number)
    except ProcessLookupError:
        return


def group_is_alive(process_group: int) -> bool:
    """
    Report whether any process remains in the group.

    Parameters:
        process_group: group id to probe.

    Returns:
        ``True`` when the group still has members.
    """
    try:
        os.killpg(process_group, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def terminate_group(process: subprocess.Popen[bytes]) -> None:
    """
    Terminate the child process group and reap the child.

    Parameters:
        process: child started with ``start_new_session=True``.

    Returns:
        None.

    Side effects: sends ``SIGTERM``, waits for the grace period, sends
    ``SIGKILL`` to survivors, and reaps the child.
    """
    process_group = process.pid
    signal_group(process_group, signal.SIGTERM)
    deadline = time.monotonic() + TERM_GRACE_SECONDS
    while time.monotonic() < deadline:
        process.poll()
        if not group_is_alive(process_group):
            return
        time.sleep(POLL_SECONDS)
    signal_group(process_group, signal.SIGKILL)
    process.wait()


def main(argv: list[str]) -> int:
    """
    Execute the command with the requested limit.

    Parameters:
        argv: process arguments, including the script name.

    Returns:
        Child exit status, ``124`` on timeout, or ``2`` on a usage error.
    """
    if len(argv) < MINIMUM_ARGUMENTS or argv[SEPARATOR_INDEX] != ARGUMENT_SEPARATOR:
        print(USAGE, file=sys.stderr)
        return EXIT_USAGE
    try:
        seconds = float(argv[SECONDS_INDEX])
    except ValueError:
        print(USAGE, file=sys.stderr)
        return EXIT_USAGE
    if seconds <= 0:
        print(USAGE, file=sys.stderr)
        return EXIT_USAGE
    command = argv[COMMAND_START_INDEX:]
    process = subprocess.Popen(command, start_new_session=True)
    try:
        return process.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        return EXIT_TIMEOUT
    finally:
        terminate_group(process)


if __name__ == TEXT_MAIN:
    sys.exit(main(sys.argv))
