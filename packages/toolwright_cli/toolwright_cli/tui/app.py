"""
Textual application for project setup.

Public API: :class:`SetupApp`, :func:`run_setup`.

Side effects: writes project files only after the user selects Apply.
"""
from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, RichLog, Select, Static

from .services import ADAPTERS, DEFAULT_COMPONENTS, PROJECT_COMPONENTS, SetupSelection, apply_selection, build_plan
from ..constants import KEY_LOCK, KEY_TARGET
from .strings import (
    COMPONENT_LABELS,
    EMPTY_STRING,
    ID_ADAPTER,
    ID_COMPONENT_PREFIX,
    ID_FORM,
    ID_LOG,
    ID_PROJECT,
    ID_STATUS,
    KEY_ADAPTER,
    TEXT_ADAPTER_LABEL,
    TEXT_APPLIED_LOG,
    TEXT_APPLY,
    TEXT_APPLY_FAILED,
    TEXT_DEFAULT_ADAPTER,
    TEXT_LOCK_LOG,
    TEXT_MCP_NOTICE,
    TEXT_PLANNED_FILES,
    TEXT_PREVIEW,
    TEXT_PREVIEW_FAILED,
    TEXT_PROJECT_DIRECTORY,
    TEXT_PROJECT_DOES_NOT_EXIST,
    TEXT_PROJECT_FILES,
    TEXT_QUIT,
    TEXT_ACTION_QUIT,
    TEXT_HASH,
    TEXT_KEY_Q,
    TEXT_VARIANT_PRIMARY,
    TEXT_VARIANT_SUCCESS,
    TEXT_SETUP_APPLIED,
    TEXT_SETUP_INITIAL,
)

ADAPTER_LABELS = [(name, name) for name in ADAPTERS]
PID_PREVIEW = "preview"
PID_APPLY = "apply"
PID_QUIT = TEXT_ACTION_QUIT


class SetupApp(App):
    """
    Interactive setup screen for one project directory.
    """

    CSS = """
    Screen { layout: vertical; }
    #form { height: auto; padding: 1 2; }
    #status { min-height: 3; padding: 1 2; }
    #log { height: 1fr; }
    Button { margin-right: 1; }
    """

    BINDINGS = [(TEXT_KEY_Q, TEXT_ACTION_QUIT, TEXT_QUIT)]

    def __init__(self, root: Path, target: Path | None = None) -> None:
        super().__init__()
        self.root = root
        self.initial_target = target or Path.cwd()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id=ID_FORM.lstrip(TEXT_HASH)):
            yield Label(TEXT_PROJECT_DIRECTORY)
            yield Input(value=str(self.initial_target), id=ID_PROJECT.lstrip(TEXT_HASH))
            yield Label(TEXT_ADAPTER_LABEL)
            yield Select(ADAPTER_LABELS, value=TEXT_DEFAULT_ADAPTER, id=KEY_ADAPTER)
            yield Label(TEXT_PROJECT_FILES)
            for component in PROJECT_COMPONENTS:
                yield Checkbox(
                    COMPONENT_LABELS[component],
                    value=component in DEFAULT_COMPONENTS,
                    id=f"{ID_COMPONENT_PREFIX.lstrip(TEXT_HASH)}{component}",
                )
            yield Button(TEXT_PREVIEW, id=PID_PREVIEW, variant=TEXT_VARIANT_PRIMARY)
            yield Button(TEXT_APPLY, id=PID_APPLY, variant=TEXT_VARIANT_SUCCESS)
            yield Button(TEXT_QUIT, id=PID_QUIT)
            yield Static(TEXT_SETUP_INITIAL, id=ID_STATUS.lstrip(TEXT_HASH))
        yield RichLog(id=ID_LOG.lstrip(TEXT_HASH), markup=False)
        yield Footer()

    def selection(self) -> SetupSelection:
        project = Path(self.query_one(ID_PROJECT, Input).value).expanduser().resolve()
        adapter = str(self.query_one(ID_ADAPTER, Select).value)
        components = tuple(
            component
            for component in PROJECT_COMPONENTS
            if self.query_one(f"{ID_COMPONENT_PREFIX}{component}", Checkbox).value
        )
        return SetupSelection(self.root, project, adapter, components)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == PID_QUIT:
            self.exit()
            return
        if event.button.id == PID_PREVIEW:
            self.preview()
            return
        if event.button.id == PID_APPLY:
            self.apply()

    def preview(self) -> None:
        status = self.query_one(ID_STATUS, Static)
        log = self.query_one(ID_LOG, RichLog)
        try:
            selection = self.selection()
            if not selection.target.is_dir():
                status.update(TEXT_PROJECT_DOES_NOT_EXIST.format(selection.target))
                return
            lines = build_plan(selection)
            log.clear()
            for line in lines:
                log.write(line)
            note = EMPTY_STRING
            if selection.adapter != TEXT_DEFAULT_ADAPTER:
                note = TEXT_MCP_NOTICE
            status.update(TEXT_PLANNED_FILES.format(len(lines), note))
        except Exception as error:
            status.update(TEXT_PREVIEW_FAILED.format(error))

    def apply(self) -> None:
        status = self.query_one(ID_STATUS, Static)
        log = self.query_one(ID_LOG, RichLog)
        try:
            selection = self.selection()
            if not selection.target.is_dir():
                status.update(TEXT_PROJECT_DOES_NOT_EXIST.format(selection.target))
                return
            result = apply_selection(selection)
            log.clear()
            log.write(TEXT_APPLIED_LOG.format(result.get(KEY_TARGET, selection.target)))
            log.write(TEXT_LOCK_LOG.format(result.get(KEY_LOCK, EMPTY_STRING)))
            status.update(TEXT_SETUP_APPLIED)
        except Exception as error:
            status.update(TEXT_APPLY_FAILED.format(error))


def run_setup(root: Path, target: Path | None = None) -> int:
    """
    Launch the setup TUI.

    Parameters:
        root: ToolWright source checkout.
        target: optional initial project directory.

    Returns:
        Zero after the application exits.

    Side effects: opens the terminal UI and may write project files.
    """
    SetupApp(root=root, target=target).run()
    return 0
