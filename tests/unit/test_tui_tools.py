"""
Tests for external tool planning in the setup TUI.
"""
from __future__ import annotations

import unittest

from tests.constants import TEXT_MAIN
from toolwright_cli.tui.tools import (
    TEXT_AST_GREP_FORMULA,
    TEXT_AST_GREP_PACKAGE,
    TEXT_BREW,
    TEXT_GLOBAL,
    TEXT_INSTALL,
    TEXT_INSTALLED,
    TEXT_MANUAL,
    TEXT_MISSING,
    TEXT_NPM,
    TEXT_PYTHON,
    TEXT_SERENA_PACKAGE,
    TEXT_SERENA_PYTHON,
    TEXT_TOOL,
    TEXT_UV,
    TOOL_AST_GREP,
    TOOL_CODEGRAPH,
    TOOL_SERENA,
    detect_tools,
    install_tools,
    plan_tool_install,
)

TEXT_DARWIN = "darwin"
TEXT_LINUX = "linux"


def which_brew(name: str) -> str | None:
    """
    Resolve brew and ast-grep only.

    Parameters:
        name: command name.

    Returns:
        A fake path or ``None``.
    """
    return name if name in (TEXT_BREW, TOOL_CODEGRAPH) else None


def which_uv(name: str) -> str | None:
    """
    Resolve uv only.

    Parameters:
        name: command name.

    Returns:
        A fake path or ``None``.
    """
    return TEXT_UV if name == TEXT_UV else None


class ToolPlanTests(unittest.TestCase):

    def test_installed_tool_returns_empty_plan(self) -> None:
        self.assertEqual(plan_tool_install(TOOL_CODEGRAPH, which=which_brew), [])

    def test_macos_prefers_brew(self) -> None:
        self.assertEqual(
            plan_tool_install(TOOL_AST_GREP, platform=TEXT_DARWIN, which=which_brew),
            [TEXT_BREW, TEXT_INSTALL, TEXT_AST_GREP_FORMULA],
        )

    def test_linux_uses_npm_for_ast_grep(self) -> None:
        self.assertEqual(
            plan_tool_install(TOOL_AST_GREP, platform=TEXT_LINUX, which=which_uv),
            None,
        )

    def test_linux_npm_plan_when_npm_exists(self) -> None:
        self.assertEqual(
            plan_tool_install(
                TOOL_AST_GREP,
                platform=TEXT_LINUX,
                which=lambda name: TEXT_NPM if name == TEXT_NPM else None,
            ),
            [TEXT_NPM, TEXT_INSTALL, TEXT_GLOBAL, TEXT_AST_GREP_PACKAGE],
        )

    def test_serena_uses_uv(self) -> None:
        self.assertEqual(
            plan_tool_install(TOOL_SERENA, platform=TEXT_LINUX, which=which_uv),
            [TEXT_UV, TEXT_TOOL, TEXT_INSTALL, TEXT_PYTHON, TEXT_SERENA_PYTHON, TEXT_SERENA_PACKAGE],
        )

    def test_codegraph_is_manual_when_missing(self) -> None:
        self.assertEqual(plan_tool_install(TOOL_CODEGRAPH, which=lambda name: None), None)
        self.assertEqual(detect_tools(lambda name: None)[TOOL_CODEGRAPH], TEXT_MISSING)
        self.assertEqual(
            install_tools([TOOL_CODEGRAPH], which=lambda name: None)[TOOL_CODEGRAPH],
            TEXT_MANUAL,
        )

    def test_installed_detection(self) -> None:
        self.assertEqual(
            install_tools([TOOL_CODEGRAPH], which=which_brew)[TOOL_CODEGRAPH],
            TEXT_INSTALLED,
        )


if __name__ == TEXT_MAIN:
    unittest.main()
