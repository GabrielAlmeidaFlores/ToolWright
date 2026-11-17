"""
External tool detection and installation for the setup TUI.

Public API: :func:`detect_tools`, :func:`plan_tool_install`, :func:`install_tools`.

Side effects: :func:`install_tools` executes package-manager commands.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable, Sequence

from ..constants import KEY_TOOL, OPERATION_INSTALL, STATUS_MISSING, TOOL_AST_GREP, TOOL_CODEGRAPH, TOOL_SERENA
from ..cli.cli_strings import KEY_MANUAL

TEXT_MANUAL = KEY_MANUAL
TEXT_INSTALLED = "installed"
TEXT_MISSING = STATUS_MISSING
TEXT_AST_GREP_FORMULA = TOOL_AST_GREP
TEXT_AST_GREP_PACKAGE = "@ast-grep/cli"
TEXT_SERENA_PACKAGE = "serena-agent"
TEXT_SERENA_PYTHON = "3.13"
TEXT_BREW = "brew"
TEXT_NPM = "npm"
TEXT_UV = "uv"
TEXT_INSTALL = OPERATION_INSTALL
TEXT_TOOL = KEY_TOOL
TEXT_GLOBAL = "-g"
TEXT_PYTHON = "-p"
TEXT_WIN_PREFIX = "win"
TEXT_CODEGRAPH_LABEL = "CodeGraph"
DEFAULT_TOOL_TIMEOUT_SECONDS = 600
TEXT_TOOL_TIMEOUT = "timed out after {} seconds"
TEXT_SERENA_LABEL = "Serena"


@dataclass(frozen=True)
class ToolSpec:
    """
    One external tool and its package-manager commands.

    Attributes:
        name: command name used for detection.
        label: human-readable name.
        commands: per-platform command templates.
        manual: whether the tool has no verified automatic installer.
    """

    name: str
    label: str
    commands: tuple[tuple[str, tuple[str, ...]], ...]
    manual: bool = False


TOOL_SPECS = (
    ToolSpec(
        TOOL_AST_GREP,
        TOOL_AST_GREP,
        (
            (TEXT_BREW, (TEXT_INSTALL, TEXT_AST_GREP_FORMULA)),
            (TEXT_NPM, (TEXT_INSTALL, TEXT_GLOBAL, TEXT_AST_GREP_PACKAGE)),
        ),
    ),
    ToolSpec(
        TOOL_SERENA,
        TEXT_SERENA_LABEL,
        ((TEXT_UV, (TEXT_TOOL, TEXT_INSTALL, TEXT_PYTHON, TEXT_SERENA_PYTHON, TEXT_SERENA_PACKAGE)),),
    ),
    ToolSpec(TOOL_CODEGRAPH, TEXT_CODEGRAPH_LABEL, (), manual=True),
)

SPECS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}


def detect_tools(which: Callable[[str], str | None] = shutil.which) -> dict[str, str]:
    """
    Report whether each managed tool is installed.

    Parameters:
        which: command lookup function.

    Returns:
        Mapping of tool name to ``installed`` or ``missing``.
    """
    return {
        spec.name: TEXT_INSTALLED if which(spec.name) else TEXT_MISSING
        for spec in TOOL_SPECS
    }


def plan_tool_install(
    name: str,
    platform: str = sys.platform,
    which: Callable[[str], str | None] = shutil.which,
) -> list[str] | None:
    """
    Build the installation command for one tool.

    Parameters:
        name: managed tool name.
        platform: ``sys.platform`` style value.
        which: command lookup function.

    Returns:
        Command argument list, or ``None`` when the tool needs a manual step.
    """
    spec = SPECS_BY_NAME[name]
    if which(spec.name):
        return []
    if spec.manual:
        return None
    for manager, command in spec.commands:
        if which(manager):
            if platform.startswith(TEXT_WIN_PREFIX) and manager == TEXT_BREW:
                continue
            return [manager, *command]
    return None


def install_tools(
    names: Sequence[str],
    platform: str = sys.platform,
    which: Callable[[str], str | None] = shutil.which,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    timeout: int = DEFAULT_TOOL_TIMEOUT_SECONDS,
) -> dict[str, str]:
    """
    Install selected tools, reporting a status for each.

    Parameters:
        names: selected tool names.
        platform: platform identifier.
        which: command lookup function.
        runner: subprocess runner.

    Returns:
        Mapping of tool name to ``installed``, ``manual``, or the failure text.
    """
    results: dict[str, str] = {}
    for name in names:
        command = plan_tool_install(name, platform=platform, which=which)
        if command is None:
            results[name] = TEXT_MANUAL
            continue
        if not command:
            results[name] = TEXT_INSTALLED
            continue
        try:
            completed = runner(command, capture_output=True, text=True, check=False, timeout=timeout)
        except subprocess.TimeoutExpired:
            results[name] = TEXT_TOOL_TIMEOUT.format(timeout)
            continue
        results[name] = TEXT_INSTALLED if completed.returncode == 0 else completed.stderr.strip()
    return results
