"""
Tests for the setup TUI planning and application services.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests import support
from tests.constants import KEY_AGENTS, KEY_CLAUDE, KEY_CODEX, KEY_COMMANDS, KEY_OPENCODE, KEY_TARGET, TEXT_MAIN, TEXT_SPACE, TEXT_TOOLWRIGHT_LOCK_JSON
from tests.unit.test_toolwright_plugin_strings import KEY_PLUGIN
from tests.integration.test_toolwright_commands_strings import TEXT_AGENTS_MD, TEXT_CLAUDE_MD

from toolwright_cli.tui.services import PLUGIN_SENTINEL, SetupSelection, apply_selection, build_plan


class SetupServiceTests(unittest.TestCase):

    def test_preview_lists_project_files_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            selection = SetupSelection(support.REPO_ROOT, target, KEY_CLAUDE, (KEY_AGENTS, KEY_COMMANDS))
            planned = build_plan(selection)
            self.assertTrue(planned)
            self.assertIn(TEXT_CLAUDE_MD, TEXT_SPACE.join(planned))
            self.assertFalse((target / TEXT_TOOLWRIGHT_LOCK_JSON).exists())

    def test_apply_writes_files_and_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            selection = SetupSelection(support.REPO_ROOT, target, KEY_CODEX, (KEY_AGENTS,))
            result = apply_selection(selection)
            self.assertTrue((target / TEXT_AGENTS_MD).is_file())
            self.assertTrue((target / TEXT_TOOLWRIGHT_LOCK_JSON).is_file())
            self.assertEqual(Path(result[KEY_TARGET]), target)

    def test_opencode_plugin_enables_its_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            selection = SetupSelection(
                support.REPO_ROOT, target, KEY_OPENCODE, (KEY_PLUGIN,)
            )
            apply_selection(selection)
            self.assertTrue((target / PLUGIN_SENTINEL).is_file())


if __name__ == TEXT_MAIN:
    unittest.main()
