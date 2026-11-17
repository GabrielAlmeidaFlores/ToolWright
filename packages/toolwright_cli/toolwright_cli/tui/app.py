"""
Textual application for project setup.

Public API: :class:`SetupApp`, :func:`run_setup`.

Side effects: writes project files only after the user selects Apply.
"""
from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, RichLog, Select, Static

from ..constants import KEY_LOCK, KEY_TARGET, KEY_TOOLS
from .services import (
    ADAPTERS,
    DEFAULT_COMPONENTS,
    PROJECT_COMPONENTS,
    TEXT_PLAN_LINE,
    SetupSelection,
    apply_selection,
    build_plan,
    tool_outcome,
)
from .strings import (
    COMPONENT_LABELS,
    EMPTY_STRING,
    ID_ADAPTER,
    ID_COMPONENT_PREFIX,
    ID_FORM,
    ID_LOG,
    ID_PROJECT,
    ID_STATUS,
    ID_TOOL_PREFIX,
    KEY_ADAPTER,
    TEXT_ACTION_QUIT,
    TEXT_ADAPTER_LABEL,
    TEXT_APPLIED_LOG,
    TEXT_APPLY,
    TEXT_APPLY_FAILED,
    TEXT_APPLY_RUNNING,
    TEXT_AST_GREP_LABEL,
    TEXT_DEFAULT_ADAPTER,
    TEXT_EXTERNAL_TOOLS,
    TEXT_HASH,
    TEXT_KEY_Q,
    TEXT_LOCK_LOG,
    TEXT_MCP_NOTICE,
    TEXT_PLANNED_FILES,
    TEXT_PREVIEW,
    TEXT_PREVIEW_FAILED,
    TEXT_PROJECT_DIRECTORY,
    TEXT_PROJECT_DOES_NOT_EXIST,
    TEXT_PROJECT_FILES,
    TEXT_QUIT,
    TEXT_SETUP_APPLIED,
    TEXT_SETUP_INITIAL,
    TEXT_SETUP_MANUAL,
    TEXT_SETUP_PARTIAL,
    TEXT_VARIANT_PRIMARY,
    TEXT_VARIANT_SUCCESS,
)
from .tools import TEXT_CODEGRAPH_LABEL, TEXT_SERENA_LABEL, TOOL_SPECS

ADAPTER_LABELS = [(name, name) for name in ADAPTERS]
TOOL_LABELS = {
    TOOL_SPECS[0].name: TEXT_AST_GREP_LABEL,
    TOOL_SPECS[1].name: TEXT_SERENA_LABEL,
    TOOL_SPECS[2].name: TEXT_CODEGRAPH_LABEL,
}
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
            yield Label(TEXT_EXTERNAL_TOOLS)
            for spec in TOOL_SPECS:
                yield Checkbox(
                    TOOL_LABELS[spec.name],
                    value=not spec.manual,
                    id=f"{ID_TOOL_PREFIX.lstrip(TEXT_HASH)}{spec.name}",
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
        tools = tuple(
            spec.name
            for spec in TOOL_SPECS
            if self.query_one(f"{ID_TOOL_PREFIX}{spec.name}", Checkbox).value
        )
        return SetupSelection(self.root, project, adapter, components, tools)

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
        try:
            selection = self.selection()
            if not selection.target.is_dir():
                status.update(TEXT_PROJECT_DOES_NOT_EXIST.format(selection.target))
                return
            self.query_one(f"{TEXT_HASH}{PID_APPLY}", Button).disabled = True
            status.update(TEXT_APPLY_RUNNING)
            self._apply_worker(selection)
        except Exception as error:
            status.update(TEXT_APPLY_FAILED.format(error))

    @work(thread=True)
    def _apply_worker(self, selection: SetupSelection) -> None:
        try:
            result = apply_selection(selection)
        except Exception as error:
            self.call_from_thread(self._apply_failed, str(error))
            return
        self.call_from_thread(self._apply_finished, selection, result)

    def _apply_finished(self, selection: SetupSelection, result: dict) -> None:
        status = self.query_one(ID_STATUS, Static)
        log = self.query_one(ID_LOG, RichLog)
        failures, manual = tool_outcome(result.get(KEY_TOOLS, {}))
        log.clear()
        log.write(TEXT_APPLIED_LOG.format(result.get(KEY_TARGET, selection.target)))
        log.write(TEXT_LOCK_LOG.format(result.get(KEY_LOCK, EMPTY_STRING)))
        for tool, tool_status in result.get(KEY_TOOLS, {}).items():
            log.write(TEXT_PLAN_LINE.format(tool, tool_status))
        if failures:
            status.update(TEXT_SETUP_PARTIAL.format(len(failures)))
        elif manual:
            status.update(TEXT_SETUP_MANUAL.format(len(manual)))
        else:
            status.update(TEXT_SETUP_APPLIED)
        self.query_one(f"{TEXT_HASH}{PID_APPLY}", Button).disabled = False

    def _apply_failed(self, message: str) -> None:
        self.query_one(ID_STATUS, Static).update(TEXT_APPLY_FAILED.format(message))
        self.query_one(f"{TEXT_HASH}{PID_APPLY}", Button).disabled = False


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
