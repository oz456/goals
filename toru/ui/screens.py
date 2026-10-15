from typing import Optional, List, Dict
from datetime import date
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label, Static, Select, RadioSet, RadioButton, OptionList
from textual.widgets.option_list import Option
from rich.markup import escape
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.binding import Binding

from ..models import Task, Project, Subtask, Priority
from ..date_utils import parse_due_date, format_due_date_badge


class TaskModal(ModalScreen[Optional[Dict]]):
    """Modal dialog for creating or editing a task."""

    DEFAULT_CSS = """
    TaskModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #task-dialog {
        width: 65;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #task-dialog-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        text-align: center;
    }

    .form-label {
        color: $text-muted;
        margin-top: 1;
    }

    .preview-label {
        color: $success;
        height: 1;
        margin-bottom: 1;
    }

    .buttons-row {
        margin-top: 1;
        height: auto;
        align: right middle;
    }

    Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, task: Optional[Task] = None, project_id: str = "inbox", title: str = "Task"):
        super().__init__()
        self.task = task
        self.project_id = project_id
        self.dialog_title = title

    def compose(self) -> ComposeResult:
        with Vertical(id="task-dialog"):
            yield Label(self.dialog_title, id="task-dialog-title")

            yield Label("Task Title:", classes="form-label")
            default_title = self.task.title if self.task else ""
            yield Input(value=default_title, placeholder="e.g. Finish quarterly report", id="task-title-input")

            yield Label("Priority:", classes="form-label")
            priority_options = [
                ("None", Priority.NONE),
                ("🔵 Low", Priority.LOW),
                ("🟡 Medium", Priority.MEDIUM),
                ("🔴 High", Priority.HIGH),
            ]
            default_priority = self.task.priority if self.task else Priority.NONE
            yield Select(
                options=priority_options,
                value=default_priority,
                allow_blank=False,
                id="task-priority-select",
            )

            yield Label("Due Date (e.g. 'today', 'tomorrow', 'friday', '2d', or YYYY-MM-DD):", classes="form-label")
            default_due = self.task.due_date if (self.task and self.task.due_date) else ""
            yield Input(value=default_due, placeholder="today, tomorrow, 3d, 1w, or clear...", id="task-due-input")
            yield Label("", id="task-due-preview", classes="preview-label")

            with Horizontal(classes="buttons-row"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Save (Enter)", variant="primary", id="btn-save")

    def on_mount(self) -> None:
        self.query_one("#task-title-input", Input).focus()
        due_input = self.query_one("#task-due-input", Input)
        if due_input.value:
            self.update_due_preview(due_input.value)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "task-due-input":
            self.update_due_preview(event.value)

    def update_due_preview(self, value: str) -> None:
        preview = self.query_one("#task-due-preview", Label)
        if not value.strip():
            preview.update("No due date set")
            return

        parsed = parse_due_date(value)
        if parsed:
            badge_text, _ = format_due_date_badge(parsed.isoformat())
            preview.update(f"Parsed: {parsed.isoformat()} ({badge_text})")
        else:
            preview.update("Could not parse date (leave blank for none)")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.save_and_exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.save_and_exit()
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def save_and_exit(self) -> None:
        title = self.query_one("#task-title-input", Input).value.strip()
        if not title:
            self.notify("Task title cannot be empty", severity="warning")
            return

        priority_val = self.query_one("#task-priority-select", Select).value
        try:
            priority = Priority(priority_val)
        except Exception:
            priority = Priority.NONE

        due_text = self.query_one("#task-due-input", Input).value.strip()
        parsed_due = parse_due_date(due_text) if due_text else None
        due_date_str = parsed_due.isoformat() if parsed_due else None

        self.dismiss({
            "title": title,
            "priority": priority,
            "due_date": due_date_str,
            "project_id": self.project_id,
        })


class ProjectModal(ModalScreen[Optional[Dict]]):
    """Modal dialog for creating or renaming a project."""

    DEFAULT_CSS = """
    ProjectModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #project-dialog {
        width: 50;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #project-dialog-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        text-align: center;
    }

    .form-label {
        color: $text-muted;
        margin-top: 1;
    }

    .buttons-row {
        margin-top: 1;
        height: auto;
        align: right middle;
    }

    Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    ICONS = ["📁", "💼", "🏠", "🚀", "🎯", "📚", "⚡", "💡", "🎨", "🔬"]

    def __init__(self, project: Optional[Project] = None, title: str = "New Project"):
        super().__init__()
        self.project = project
        self.dialog_title = title

    def compose(self) -> ComposeResult:
        with Vertical(id="project-dialog"):
            yield Label(self.dialog_title, id="project-dialog-title")

            yield Label("Project Name:", classes="form-label")
            default_name = self.project.name if self.project else ""
            yield Input(value=default_name, placeholder="e.g. Side Hustle", id="project-name-input")

            yield Label("Icon:", classes="form-label")
            icon_options = [(f"{icon}  {icon}", icon) for icon in self.ICONS]
            default_icon = self.project.icon if (self.project and self.project.icon) else "📁"
            yield Select(
                options=icon_options,
                value=default_icon,
                allow_blank=False,
                id="project-icon-select",
            )

            with Horizontal(classes="buttons-row"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Save", variant="primary", id="btn-save")

    def on_mount(self) -> None:
        self.query_one("#project-name-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.save_and_exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.save_and_exit()
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def save_and_exit(self) -> None:
        name = self.query_one("#project-name-input", Input).value.strip()
        if not name:
            self.notify("Project name cannot be empty", severity="warning")
            return

        icon = self.query_one("#project-icon-select", Select).value or "📁"
        self.dismiss({
            "name": name,
            "icon": icon,
        })


class QuickDueDateModal(ModalScreen[Optional[str]]):
    """Fast inline modal for changing a task's due date."""

    DEFAULT_CSS = """
    QuickDueDateModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #due-dialog {
        width: 52;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #due-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .preview-label {
        color: $success;
        height: 1;
        margin-top: 1;
    }

    .quick-hints {
        color: $text-muted;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, current_due: Optional[str] = None):
        super().__init__()
        self.current_due = current_due or ""

    def compose(self) -> ComposeResult:
        with Vertical(id="due-dialog"):
            yield Label("📅 Set Due Date", id="due-title")
            yield Input(
                value=self.current_due,
                placeholder="today, tomorrow, friday, 2d, 1w, or 'none'",
                id="due-input",
            )
            yield Label("", id="due-preview", classes="preview-label")
            yield Label("Hints: [b]today[/], [b]tomorrow[/], [b]fri[/], [b]+3d[/], [b]none[/] (clears)", classes="quick-hints")
            with Horizontal(classes="buttons-row"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Save (Enter)", variant="primary", id="btn-save")

    def on_mount(self) -> None:
        input_widget = self.query_one("#due-input", Input)
        input_widget.focus()
        if self.current_due:
            self.update_preview(self.current_due)

    def on_input_changed(self, event: Input.Changed) -> None:
        self.update_preview(event.value)

    def update_preview(self, value: str) -> None:
        preview = self.query_one("#due-preview", Label)
        if not value.strip() or value.strip().lower() in ("none", "clear"):
            preview.update("No due date (cleared)")
            return

        parsed = parse_due_date(value)
        if parsed:
            badge_text, _ = format_due_date_badge(parsed.isoformat())
            preview.update(f"-> {parsed.isoformat()} ({badge_text})")
        else:
            preview.update("Unrecognized format (leave blank to clear)")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.save_and_exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.save_and_exit()
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def save_and_exit(self) -> None:
        val = self.query_one("#due-input", Input).value.strip()
        if not val or val.lower() in ("none", "clear"):
            self.dismiss("")
            return

        parsed = parse_due_date(val)
        if parsed:
            self.dismiss(parsed.isoformat())
        else:
            self.notify("Invalid date format", severity="warning")


class SubtaskModal(ModalScreen[List[Subtask]]):
    """Modal for managing subtasks under a task."""

    DEFAULT_CSS = """
    SubtaskModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #subtask-dialog {
        width: 60;
        height: 24;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #subtask-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #subtask-options {
        height: 12;
        border: solid $surface-lighten-1;
        margin-bottom: 1;
    }

    .help-hint {
        color: $text-muted;
        font-size: 80%;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("space", "toggle_subtask", "Toggle Completed"),
        Binding("d", "delete_subtask", "Delete Subtask"),
        Binding("delete", "delete_subtask", "Delete Subtask"),
    ]

    def __init__(self, task: Task):
        super().__init__()
        self.task_title = task.title
        # Make a copy of subtasks
        self.subtasks = [Subtask(id=s.id, title=s.title, completed=s.completed) for s in task.subtasks]

    def compose(self) -> ComposeResult:
        with Vertical(id="subtask-dialog"):
            yield Label(f"Subtasks: {self.task_title}", id="subtask-title")
            yield OptionList(id="subtask-options")
            yield Label("[Space]: Toggle   [d]/[Del]: Remove   [Esc]: Done", classes="help-hint")
            yield Label("Add new subtask:", classes="form-label")
            yield Input(placeholder="Type subtask name and hit Enter...", id="new-subtask-input")
            with Horizontal(classes="buttons-row"):
                yield Button("Done (Esc)", variant="primary", id="btn-done")

    def on_mount(self) -> None:
        self.refresh_options()
        self.query_one("#new-subtask-input", Input).focus()

    def refresh_options(self) -> None:
        opt_list = self.query_one("#subtask-options", OptionList)
        opt_list.clear_options()
        for idx, s in enumerate(self.subtasks):
            check = "✔ " if s.completed else "◻ "
            style = "strike dim" if s.completed else ""
            opt_list.add_option(Option(f"{check} {escape(s.title)}", id=str(idx)))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        title = event.value.strip()
        if title:
            self.subtasks.append(Subtask(title=title))
            event.input.value = ""
            self.refresh_options()

    def action_toggle_subtask(self) -> None:
        opt_list = self.query_one("#subtask-options", OptionList)
        idx = opt_list.highlighted
        if idx is not None and 0 <= idx < len(self.subtasks):
            self.subtasks[idx].completed = not self.subtasks[idx].completed
            self.refresh_options()
            opt_list.highlighted = idx

    def action_delete_subtask(self) -> None:
        opt_list = self.query_one("#subtask-options", OptionList)
        idx = opt_list.highlighted
        if idx is not None and 0 <= idx < len(self.subtasks):
            self.subtasks.pop(idx)
            self.refresh_options()
            if self.subtasks:
                opt_list.highlighted = min(idx, len(self.subtasks) - 1)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.action_close()

    def action_close(self) -> None:
        self.dismiss(self.subtasks)


class ConfirmModal(ModalScreen[bool]):
    """Confirmation modal for deletions."""

    DEFAULT_CSS = """
    ConfirmModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #confirm-dialog {
        width: 48;
        height: auto;
        border: thick $error;
        background: $surface;
        padding: 1 2;
    }

    #confirm-msg {
        text-align: center;
        margin-top: 1;
        margin-bottom: 1;
        color: $text;
    }

    .buttons-row {
        align: center middle;
        height: auto;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
    ]

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label(self.message, id="confirm-msg")
            with Horizontal(classes="buttons-row"):
                yield Button("Cancel (n)", variant="default", id="btn-cancel")
                yield Button("Delete (y)", variant="error", id="btn-confirm")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class HelpModal(ModalScreen[None]):
    """Cheatsheet modal displaying all controls and shortcuts."""

    DEFAULT_CSS = """
    HelpModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.75);
    }

    #help-dialog {
        width: 76;
        height: 28;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #help-title {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin-bottom: 1;
    }

    #help-content {
        height: 1fr;
        overflow-y: auto;
    }

    .help-section {
        color: $primary;
        text-style: bold;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss_help", "Close"),
        Binding("q", "dismiss_help", "Close"),
        Binding("?", "dismiss_help", "Close"),
    ]

    HELP_TEXT = """
[bold #89b4fa]🧭 NAVIGATION & FOCUS[/]
  [b]Tab[/] or [b]← / →[/] or [b]h / l[/]  Switch between Projects & Tasks panes
  [b]↑ / ↓[/] or [b]j / k[/]            Move selection up / down
  [b]Home / End[/] or [b]g / G[/]        Jump to top / bottom
  [b]Mouse Click[/]                 Select any project or task directly

[bold #a6e3a1]⚡ TASK CONTROLS[/]
  [b]Space[/]                     Toggle task completion (✔ / ◻)
  [b]n[/] or [b]a[/]                  Add a new task (or project)
  [b]e[/] or [b]Enter[/]              Edit highlighted task (or rename project)
  [b]d[/] or [b]Delete[/]             Delete highlighted task (or project)
  [b]1 / 2 / 3 / 4[/]             Set Priority (1=🔴High, 2=🟡Med, 3=🔵Low, 4=None)
  [b]t[/]                         Quick Due Date popup
  [b]s[/]                         Subtasks manager (view/add/check subtasks)

[bold #f9e2af]🔍 SEARCH & GENERAL[/]
  [b]/[/]                         Open live filter/search bar
  [b]?[/]                         Toggle this Help cheatsheet
  [b]q[/]                         Quit Toru cleanly

[bold #cba6f7]📅 DUE DATE SYNTAX[/]
  Works with friendly terms: [b]today[/], [b]tomorrow[/], [b]friday[/], [b]+2d[/], [b]1w[/], [b]none[/]
"""

    def compose(self) -> ComposeResult:
        with Vertical(id="help-dialog"):
            yield Label("TORU Quick Reference", id="help-title")
            with Vertical(id="help-content"):
                yield Static(self.HELP_TEXT)
            with Horizontal(classes="buttons-row"):
                yield Button("Close (Esc)", variant="primary", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)

    def action_dismiss_help(self) -> None:
        self.dismiss(None)
