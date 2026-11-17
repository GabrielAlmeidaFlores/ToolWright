"""
Integration tests for validation entry points.

These tests execute the real shell and Python entry points. They require no
network access and no model credentials.
"""
from __future__ import annotations
from tests.integration.test_entrypoints_strings import (
    TEXT_PATH_SUFFIX,
    TEXT_TASK_ERROR,
)
from tests.integration.test_entrypoints_strings import (
    FLAG_ALL,
    FLAG_ARM,
    FLAG_DRY_RUN,
    FLAG_ONLY,
    FLAG_TARGET,
    FLAG_TASK,
    FLAG_WORKSPACE,
    KEY_AGENTS,
    KEY_BASELINE,
    KEY_BASH,
    KEY_COORDINATOR_SLIM,
    KEY_DIRECT_SLIM,
    KEY_NONSENSE,
    KEY_OPTIMIZED,
    KEY_PROJECT,
    KEY_PYTHON3,
    KEY_SLIM_UNCAPPED,
    KEY_TOOLS_ON_DEMAND,
    TEXT_ADAPTER_DISCOVERY_HEADER,
    TEXT_AGENT_FLAG,
    TEXT_CHECKED_D,
    TEXT_DEFAULT_MODE_MUST_NOT_CREATE_THE_TARGET,
    TEXT_HOME,
    TEXT_JSON,
    TEXT_MAIN,
    TEXT_MISSING_JSON,
    TEXT_OK,
    TEXT_OPENCODE_AGENTS_BACKEND_MD,
    TEXT_PATH,
    TEXT_SCRIPTS_INSTALLATION_INSTALL_SH,
    TEXT_SCRIPTS_VALIDATION_CHECK_ADAPTER_DISCOVERY_SH,
    TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY,
    TEXT_SCRIPTS_VALIDATION_VALIDATE_SH,
    TEXT_TASK_NOT_FOUND,
    TEXT_TOOLWRIGHT_INSTALL,
    TEXT_UNKNOWN_ARM,
    TEXT_WOULD_COPY,
    TEXT_WOULD_RUN,
)

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.constants import EMPTY_STRING, KEY_COORDINATOR, TEXT_BACKEND_DEVELOPER, TEXT_OPENCODE, TEXT_OPENCODE_AGENTS_COORDINATOR_MD, TEXT_OPENCODE_JSONC, TEXT_UTF_8

from tests import support
from tests.unit.test_toolwright_plugin_strings import TEXT_OPENCODE_PLUGINS_TOOLWRIGHT_MEMORY_JS

REPO_ROOT = support.REPO_ROOT
PYTHON_BIN = Path(sys.executable).parent
SAFE_PATH = str(PYTHON_BIN) + TEXT_PATH_SUFFIX


class ValidationEntryPointTests(unittest.TestCase):

    def test_validate_config_script_passes(self) -> None:
        result = subprocess.run(
            [KEY_PYTHON3, TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(TEXT_OK, result.stdout)

    def test_adapter_discovery_entrypoint_passes(self) -> None:
        result = subprocess.run(
            [KEY_BASH, TEXT_SCRIPTS_VALIDATION_CHECK_ADAPTER_DISCOVERY_SH],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(TEXT_ADAPTER_DISCOVERY_HEADER, result.stdout)

    def test_validate_shell_entrypoint_passes(self) -> None:
        result = subprocess.run(
            [KEY_BASH, TEXT_SCRIPTS_VALIDATION_VALIDATE_SH],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_reports_checked_count(self) -> None:
        result = subprocess.run(
            [KEY_PYTHON3, TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        self.assertRegex(result.stdout, TEXT_CHECKED_D)


class InstallationDryRunTests(unittest.TestCase):

    def test_default_mode_is_check_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_INSTALL) as directory:
            target = Path(directory) / KEY_PROJECT
            result = subprocess.run(
                [KEY_BASH, TEXT_SCRIPTS_INSTALLATION_INSTALL_SH, FLAG_TARGET, str(target)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(target.exists(), TEXT_DEFAULT_MODE_MUST_NOT_CREATE_THE_TARGET)

    def test_all_includes_the_memory_plugin(self) -> None:
        with tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_INSTALL) as directory:
            target = Path(directory) / KEY_PROJECT
            result = subprocess.run(
                [KEY_BASH, TEXT_SCRIPTS_INSTALLATION_INSTALL_SH, FLAG_DRY_RUN, FLAG_ALL, FLAG_TARGET, str(target)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(TEXT_OPENCODE_PLUGINS_TOOLWRIGHT_MEMORY_JS, result.stdout)

    def test_dry_run_lists_planned_actions(self) -> None:
        with tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_INSTALL) as directory:
            target = Path(directory) / KEY_PROJECT
            result = subprocess.run(
                [KEY_BASH, TEXT_SCRIPTS_INSTALLATION_INSTALL_SH, FLAG_DRY_RUN, FLAG_ONLY, KEY_AGENTS, FLAG_TARGET, str(target)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(KEY_AGENTS, result.stdout)
            self.assertFalse(target.exists())


if __name__ == TEXT_MAIN:
    unittest.main()
