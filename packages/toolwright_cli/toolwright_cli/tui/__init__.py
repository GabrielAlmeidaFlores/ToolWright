"""
Textual setup frontend for ToolWright.

Public API: :func:`run_setup`.

Side effects: imports Textual lazily; no files are written until the user
selects Apply.
"""
from __future__ import annotations

from .services import SetupSelection, build_plan, apply_selection

EXPORT_SETUP_SELECTION = "SetupSelection"
EXPORT_BUILD_PLAN = "build_plan"
EXPORT_APPLY = "apply_selection"

__all__ = [EXPORT_SETUP_SELECTION, EXPORT_BUILD_PLAN, EXPORT_APPLY]
