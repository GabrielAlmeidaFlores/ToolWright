"""
Unit tests for the benchmark command timeout wrapper.

Public API: none. The module is a unittest test case.

Side effects: starts short-lived local processes only; no network access.
"""
from __future__ import annotations

from tests.constants import EMPTY_STRING, KEY_BASH, TEXT_MAIN

import subprocess
import sys
import time
import unittest

from tests import support

TEXT_SCRIPT = 'scripts/benchmarking/run_with_timeout.py'
TEXT_ARGUMENT_SEPARATOR = '--'
TEXT_PYTHON_COMMAND_FLAG = '-c'
TEXT_SLEEP_FOREVER = 'import time; time.sleep(30)'
TEXT_EXIT_THREE = 'import sys; sys.exit(3)'
TEXT_SLEEP_COMMAND = 'sleep 3371'
TEXT_BACKGROUND_SLEEP = '{ sleep 3371; } & exit 0'
TEXT_PGREP = 'pgrep'
TEXT_PGREP_FULL_COMMAND_LINE = '-f'
TIMEOUT_SECONDS = '0.2'
GENEROUS_SECONDS = '20'
EXPECTED_TIMEOUT_EXIT = 124
EXPECTED_USAGE_EXIT = 2
EXPECTED_CHILD_EXIT = 3
EXPECTED_SUCCESS_EXIT = 0
CLEANUP_POLL_SECONDS = 0.5


def run_wrapper(*arguments: str) -> subprocess.CompletedProcess[str]:
    """
    Execute the wrapper with the given arguments.

    Parameters:
        arguments: arguments passed after the script path.

    Returns:
        Completed process with captured text output.
    """
    return subprocess.run(
        [sys.executable, str(support.REPO_ROOT / TEXT_SCRIPT), *arguments],
        cwd=support.REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


class BenchmarkTimeoutTests(unittest.TestCase):

    def test_returns_child_exit_status(self) -> None:
        result = run_wrapper(
            GENEROUS_SECONDS,
            TEXT_ARGUMENT_SEPARATOR,
            sys.executable,
            TEXT_PYTHON_COMMAND_FLAG,
            TEXT_EXIT_THREE,
        )
        self.assertEqual(result.returncode, EXPECTED_CHILD_EXIT, result.stderr)

    def test_returns_timeout_status(self) -> None:
        result = run_wrapper(
            TIMEOUT_SECONDS,
            TEXT_ARGUMENT_SEPARATOR,
            sys.executable,
            TEXT_PYTHON_COMMAND_FLAG,
            TEXT_SLEEP_FOREVER,
        )
        self.assertEqual(result.returncode, EXPECTED_TIMEOUT_EXIT, result.stderr)

    def test_rejects_missing_separator(self) -> None:
        result = run_wrapper(GENEROUS_SECONDS, sys.executable, TEXT_PYTHON_COMMAND_FLAG, TEXT_EXIT_THREE)
        self.assertEqual(result.returncode, EXPECTED_USAGE_EXIT)

    def test_terminates_group_members_after_the_child_exits(self) -> None:
        result = run_wrapper(GENEROUS_SECONDS, TEXT_ARGUMENT_SEPARATOR, KEY_BASH, TEXT_PYTHON_COMMAND_FLAG, TEXT_BACKGROUND_SLEEP)
        self.assertEqual(result.returncode, EXPECTED_SUCCESS_EXIT, result.stderr)
        time.sleep(CLEANUP_POLL_SECONDS)
        survivors = subprocess.run(
            [TEXT_PGREP, TEXT_PGREP_FULL_COMMAND_LINE, TEXT_SLEEP_COMMAND],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(survivors.stdout.strip(), EMPTY_STRING)


if __name__ == TEXT_MAIN:
    unittest.main()
