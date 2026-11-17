"""
Setup planning and application services for the TUI.

Public API: :class:`SetupSelection`, :func:`build_plan`, :func:`apply_selection`.

Side effects: :func:`apply_selection` writes project files through the installer.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .. import installer
from ..constants import KEY_AGENTS, KEY_COMMANDS, KEY_PLUGIN, KEY_RALPH, KEY_SKILLS, PLATFORM_CHOICES
from ..cli.cli_strings import TEMPLATE_TEMPLATE_3

DEFAULT_PROFILE = "tui"
PROJECT_COMPONENTS = (KEY_AGENTS, KEY_COMMANDS, KEY_SKILLS, KEY_RALPH, KEY_PLUGIN)
ADAPTERS = PLATFORM_CHOICES
TEXT_PLAN_LINE = TEMPLATE_TEMPLATE_3


@dataclass(frozen=True)
class SetupSelection:
    """
    One setup request.

    Attributes:
        root: ToolWright source checkout.
        target: Project directory that receives generated files.
        adapter: Adapter name.
        components: Selected component names.
    """

    root: Path
    target: Path
    adapter: str
    components: tuple[str, ...]


def build_plan(selection: SetupSelection) -> list[str]:
    """
    Return human-readable planned file actions without writing anything.

    Parameters:
        selection: validated setup selection.

    Returns:
        One line per planned file.

    Side effects: reads source and target files only.
    """
    planned = installer.plan_files(
        selection.root,
        selection.target,
        list(selection.components),
        adapter=selection.adapter,
    )
    return [
        TEXT_PLAN_LINE.format(item.component, item.destination)
        for item in planned
    ]


def apply_selection(selection: SetupSelection) -> dict:
    """
    Apply one setup selection and return the installer result.

    Parameters:
        selection: validated setup selection.

    Returns:
        Installer result dictionary.

    Side effects: writes generated files and the lock file.
    """
    return installer.install(
        root=selection.root,
        target=selection.target,
        profile=DEFAULT_PROFILE,
        components=list(selection.components),
        apply=True,
        adapter=selection.adapter,
    )
