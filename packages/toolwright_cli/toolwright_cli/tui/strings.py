"""
String constants for the setup TUI.

Public API: module constants only.

Side effects: none.
"""
from __future__ import annotations

from ..constants import DEFAULT_ADAPTER, EMPTY_STRING, KEY_ADAPTER, KEY_AGENTS, KEY_COMMANDS, KEY_PLUGIN, KEY_RALPH, KEY_SKILLS, TEXT_TEXT_3
from ..compat_strings import TEXT_SKILLS as TEXT_SKILLS_LABEL
from ..governance_strings import KEY_PRIMARY

TEXT_ADAPTER_LABEL = "Target adapter"
TEXT_AGENTS_LABEL = "Agents"
TEXT_APPLY = "Apply"
TEXT_APPLY_FAILED = "Apply failed: {}"
TEXT_COMMANDS_LABEL = "Commands"
TEXT_DEFAULT_ADAPTER = DEFAULT_ADAPTER
TEXT_MCP_NOTICE = " MCP configuration is not generated for this adapter."
TEXT_MEMORY_PLUGIN_LABEL = "Memory plugin"
TEXT_PLANNED_FILES = "{} planned file(s).{}"
TEXT_PREVIEW = "Preview"
TEXT_PREVIEW_FAILED = "Preview failed: {}"
TEXT_PROJECT_DIRECTORY = "Project directory"
TEXT_PROJECT_DOES_NOT_EXIST = "Project directory does not exist: {}"
TEXT_PROJECT_FILES = "Project files"
TEXT_QUIT = "Quit"
TEXT_RALPH_LABEL = "Ralph (optional)"
TEXT_SETUP_APPLIED = "Setup applied. Run toolwright doctor to verify."
TEXT_SETUP_INITIAL = "Select a project and preview the plan."
TEXT_APPLIED_LOG = "applied: {}"
TEXT_LOCK_LOG = "lock: {}"

ID_ADAPTER = "#adapter"
ID_COMPONENT_PREFIX = "#component-"
ID_PROJECT = "#project"
ID_STATUS = "#status"
ID_LOG = "#log"
ID_FORM = "#form"

COMPONENT_LABELS = {
    KEY_AGENTS: TEXT_AGENTS_LABEL,
    KEY_COMMANDS: TEXT_COMMANDS_LABEL,
    KEY_SKILLS: TEXT_SKILLS_LABEL,
    KEY_RALPH: TEXT_RALPH_LABEL,
    KEY_PLUGIN: TEXT_MEMORY_PLUGIN_LABEL,
}

TEXT_HASH = TEXT_TEXT_3
TEXT_KEY_Q = "q"
TEXT_ACTION_QUIT = "quit"
TEXT_VARIANT_PRIMARY = KEY_PRIMARY
TEXT_VARIANT_SUCCESS = "success"
