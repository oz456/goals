from textual.widgets import OptionList, Static
from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.app import ComposeResult
from textual.binding import Binding


class GoalsListWidget(OptionList):
    """Left pane: Major goals list."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "enter_workspace", "Enter Workspace", show=False),
        Binding("right", "enter_workspace", "Enter Workspace", show=False),
        Binding("l", "enter_workspace", "Enter Workspace", show=False),
        Binding("shift+up", "move_item_up", "Move Goal Up", show=False),
        Binding("shift+down", "move_item_down", "Move Goal Down", show=False),
        Binding("K", "move_item_up", "Move Goal Up", show=False),
        Binding("J", "move_item_down", "Move Goal Down", show=False),
    ]

    def action_enter_workspace(self) -> None:
        self.app.action_enter_workspace()

    def action_move_item_up(self) -> None:
        self.app.action_move_item_up()

    def action_move_item_down(self) -> None:
        self.app.action_move_item_down()


class WorkspaceListWidget(OptionList):
    """Right pane: Specific short-term goals for active major goal."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("escape", "exit_workspace", "Back to Goals", show=False),
        Binding("left", "exit_workspace", "Back to Goals", show=False),
        Binding("h", "exit_workspace", "Back to Goals", show=False),
        Binding("shift+up", "move_item_up", "Move Goal Up", show=False),
        Binding("shift+down", "move_item_down", "Move Goal Down", show=False),
        Binding("K", "move_item_up", "Move Goal Up", show=False),
        Binding("J", "move_item_down", "Move Goal Down", show=False),
    ]

    def action_exit_workspace(self) -> None:
        self.app.action_exit_workspace()

    def action_move_item_up(self) -> None:
        self.app.action_move_item_up()

    def action_move_item_down(self) -> None:
        self.app.action_move_item_down()


class HelpScreen(ModalScreen):
    """Detailed help modal displaying all shortcuts."""

    def __init__(self, theme: dict):
        super().__init__()
        self.theme = theme

    def compose(self) -> ComposeResult:
        with Vertical(id="help-dialog"):
            yield Static("GOALS  •  KEYBOARD SHORTCUTS", id="help-title")

            with Vertical(id="help-content"):
                yield Static("[bold]NAVIGATION[/]", classes="help-section")
                yield Static("  [bold]↑ / ↓[/] or [bold]j / k[/]          Move cursor up / down", classes="help-row")
                yield Static("  [bold]Shift + ↑ / ↓[/] or [bold]K / J[/]  Rearrange item up / down in pane", classes="help-row")
                yield Static("  [bold]Enter[/] or [bold]→ / l[/]          Open Workspace (step into right pane)", classes="help-row")
                yield Static("  [bold]Esc[/] or [bold]← / h[/]            Back to Major Goals (step back to left pane)", classes="help-row")
                yield Static("  [bold]Tab[/]                     Switch between Left and Right panes", classes="help-row")

                yield Static("[bold]GOALS & TASKS[/]", classes="help-section")
                yield Static("  [bold]Space[/]                   Toggle completion (✔ / ◻)", classes="help-row")
                yield Static("  [bold]n[/] or [bold]a[/]                  Add new goal / task inline", classes="help-row")
                yield Static("  [bold]e[/]                       Edit highlighted item inline", classes="help-row")
                yield Static("  [bold]dd[/] or [bold]Delete[/]            Delete highlighted item (quick double-tap)", classes="help-row")

                yield Static("[bold]WINDOWS / WORKSPACES[/]", classes="help-section")
                yield Static("  [bold]Alt + t[/]                 Create a new window tab", classes="help-row")
                yield Static("  [bold]Alt + 1..9[/]              Jump directly to window tab", classes="help-row")
                yield Static("  [bold]Alt + ← / →[/] or [bold][ / ][/]   Switch previous / next window tab", classes="help-row")
                yield Static("  [bold]Alt + Shift + ← / →[/]     Rearrange active window tab left / right", classes="help-row")
                yield Static("  [bold]Alt + H / L[/]             Rearrange active window tab left / right", classes="help-row")
                yield Static("  [bold]Alt + r[/]                 Rename active window", classes="help-row")
                yield Static("  [bold]Alt + w[/]                 Close active window (keeps at least 1)", classes="help-row")

                yield Static("[bold]GENERAL[/]", classes="help-section")
                yield Static("  [bold]?[/]                       Toggle this help screen", classes="help-row")
                yield Static("  [bold]q[/]                       Quit", classes="help-row")

            yield Static("[dim]Press Esc, ?, or q to close[/]", id="help-footer")

    def on_mount(self) -> None:
        bg = self.theme.get("background", "#0d0d0d")
        fg = self.theme.get("foreground", "#f5f5f5")
        muted = self.theme.get("muted", "#5c5c5c")
        accent = self.theme.get("accent", "#e63946")

        try:
            dialog = self.query_one("#help-dialog")
            dialog.styles.background = bg
            dialog.styles.border = ("tall", accent)
            dialog.styles.color = fg

            self.query_one("#help-title").styles.color = accent
            for s in self.query(".help-section"):
                s.styles.color = accent
            self.query_one("#help-footer").styles.color = muted
        except Exception:
            pass

    def on_key(self, event) -> None:
        if event.key in ("escape", "question_mark", "q", "enter", "space", "f1"):
            event.stop()
            self.dismiss()

    def on_click(self, event) -> None:
        self.dismiss()
