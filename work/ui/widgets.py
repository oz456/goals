from textual.widgets import OptionList
from textual.binding import Binding


class GoalsListWidget(OptionList):
    """Left pane: Major goals list."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "enter_workspace", "Enter Workspace", show=False),
        Binding("right", "enter_workspace", "Enter Workspace", show=False),
        Binding("l", "enter_workspace", "Enter Workspace", show=False),
    ]

    def action_enter_workspace(self) -> None:
        self.app.action_enter_workspace()


class WorkspaceListWidget(OptionList):
    """Right pane: Specific short-term goals for active major goal."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("escape", "exit_workspace", "Back to Goals", show=False),
        Binding("left", "exit_workspace", "Back to Goals", show=False),
        Binding("h", "exit_workspace", "Back to Goals", show=False),
    ]

    def action_exit_workspace(self) -> None:
        self.app.action_exit_workspace()
