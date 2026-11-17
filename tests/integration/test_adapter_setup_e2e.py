"""
End-to-end setup tests for every supported adapter.

Each case installs, checks, and uninstalls the adapter through the real CLI.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import support
from tests.constants import KEY_OPENCODE, TEXT_MAIN, TEXT_OPENCODE, TEXT_OPENCODE_JSONC, TEXT_TOOLWRIGHT_LOCK_JSON
from tests.integration.test_toolwright_commands_strings import (
    FLAG_APPLY,
    FLAG_CHECK,
    FLAG_PLATFORM,
    FLAG_PROFILE,
    FLAG_TARGET,
    FLAG_YES,
    KEY_CLAUDE,
    KEY_CODEX,
    KEY_COPILOT,
    KEY_MINIMAL,
    KEY_INSTALL,
    KEY_TOOLWRIGHT_CLI,
    KEY_UNINSTALL,
    KEY_UPDATE,
    TEXT_AGENTS_MD,
    TEXT_CLAUDE_MD,
    TEXT_COPILOT_INSTRUCTIONS,
    TEXT_M,
    TEXT_PYTHONPATH,
)

CLI = (sys.executable, TEXT_M, KEY_TOOLWRIGHT_CLI)
ADAPTER_CASES = (
    (KEY_CLAUDE, TEXT_CLAUDE_MD),
    (KEY_COPILOT, TEXT_COPILOT_INSTRUCTIONS),
    (KEY_CODEX, TEXT_AGENTS_MD),
)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """
    Run the installed-module CLI from the repository checkout.

    Parameters:
        args: command arguments.

    Returns:
        Completed process.

    Side effects: executes the CLI subprocess.
    """
    environment = dict(os.environ)
    environment[TEXT_PYTHONPATH] = str(support.CLI_PACKAGE)
    return subprocess.run(
        [*CLI, *args],
        cwd=support.REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
        env=environment,
    )


class AdapterSetupEndToEndTests(unittest.TestCase):

    def test_each_adapter_installs_updates_and_uninstalls(self) -> None:
        for adapter, marker in ADAPTER_CASES:
            with self.subTest(adapter=adapter), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                install = run_cli(
                    KEY_INSTALL, FLAG_PLATFORM, adapter, FLAG_PROFILE, KEY_MINIMAL,
                    FLAG_TARGET, str(target), FLAG_APPLY,
                )
                self.assertEqual(install.returncode, 0, install.stderr)
                self.assertTrue((target / marker).is_file(), marker)
                self.assertTrue((target / TEXT_TOOLWRIGHT_LOCK_JSON).is_file())

                update = run_cli(KEY_UPDATE, FLAG_CHECK, FLAG_TARGET, str(target))
                self.assertEqual(update.returncode, 0, update.stderr)

                uninstall = run_cli(
                    KEY_UNINSTALL, FLAG_TARGET, str(target), FLAG_APPLY, FLAG_YES,
                )
                self.assertEqual(uninstall.returncode, 0, uninstall.stderr)
                self.assertFalse((target / marker).exists(), marker)

    def test_opencode_adapter_installs_and_uninstalls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            install = run_cli(
                KEY_INSTALL, FLAG_PLATFORM, KEY_OPENCODE, FLAG_PROFILE, KEY_MINIMAL,
                FLAG_TARGET, str(target), FLAG_APPLY,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            self.assertTrue((target / TEXT_OPENCODE / TEXT_OPENCODE_JSONC).is_file())
            uninstall = run_cli(
                KEY_UNINSTALL, FLAG_TARGET, str(target), FLAG_APPLY, FLAG_YES,
            )
            self.assertEqual(uninstall.returncode, 0, uninstall.stderr)


if __name__ == TEXT_MAIN:
    unittest.main()
