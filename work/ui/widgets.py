from textual.widgets import OptionList
from textual.binding import Binding


class ProjectListWidget(OptionList):
    """Left pane for projects and smart views."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g", "first", "Top", show=False),
        Binding("G", "last", "Bottom", show=False),
        Binding("right", "focus_tasks", "Focus Tasks", show=False),
        Binding("l", "focus_tasks", "Focus Tasks", show=False),
        Binding("enter", "focus_tasks", "Focus Tasks", show=False),
    ]

    def action_focus_tasks(self) -> None:
        self.app.action_focus_tasks()


class TaskListWidget(OptionList):
    """Right pane for tasks."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g", "first", "Top", show=False),
        Binding("G", "last", "Bottom", show=False),
        Binding("left", "focus_projects", "Focus Projects", show=False),
        Binding("h", "focus_projects", "Focus Projects", show=False),
    ]

    def action_focus_projects(self) -> None:
        self.app.action_focus_projects()
