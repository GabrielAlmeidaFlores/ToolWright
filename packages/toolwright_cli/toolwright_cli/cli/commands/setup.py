"""
Setup command handler.

Public API: :func:`_command_setup`.

Side effects: launches the Textual setup application and may write project files.
"""
from __future__ import annotations

import argparse

from ...paths import ToolWrightError, resolve_target
from ..common import resolve_repository_root

TEXT_TEXTUAL_NOT_INSTALLED = (
    "the setup TUI requires the optional Textual dependency; "
    "install it with: uv tool install 'toolwright-cli[tui]'"
)


def _command_setup(args: argparse.Namespace) -> int:
    try:
        from ...tui.app import run_setup
    except ImportError as error:
        raise ToolWrightError(TEXT_TEXTUAL_NOT_INSTALLED) from error
    return run_setup(root=resolve_repository_root(args), target=resolve_target(args.target))
