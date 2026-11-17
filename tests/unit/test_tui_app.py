"""
Headless smoke tests for the Textual setup application.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests import support
from tests.constants import KEY_AGENTS, KEY_OPENCODE, TEXT_MAIN
from tests.unit.test_toolwright_plugin_strings import KEY_PLUGIN
from toolwright_cli.tui.tools import TOOL_CODEGRAPH

TEXT_TEXTUAL_IS_NOT_INSTALLED = "Textual is not installed"

try:
    from textual.app import App
except ImportError:
    App = None


@unittest.skipIf(App is None, TEXT_TEXTUAL_IS_NOT_INSTALLED)
class SetupAppTests(unittest.IsolatedAsyncioTestCase):

    async def test_app_starts_and_exposes_the_selection(self) -> None:
        from toolwright_cli.tui.app import SetupApp

        with tempfile.TemporaryDirectory() as directory:
            app = SetupApp(root=support.REPO_ROOT, target=Path(directory))
            async with app.run_test() as pilot:
                await pilot.pause()
                selection = app.selection()
                self.assertEqual(selection.adapter, KEY_OPENCODE)
                self.assertIn(KEY_AGENTS, selection.components)
                self.assertIn(KEY_PLUGIN, selection.components)
                self.assertNotIn(TOOL_CODEGRAPH, selection.tools)


if __name__ == TEXT_MAIN:
    unittest.main()
