import time
from typing import List, Optional
from rich.markup import escape
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Input, Label
from textual.widgets.option_list import Option
from textual.events import DescendantFocus

from ..models import Goal, GoalItem
from ..storage import Storage
from ..theme import load_theme, generate_css, get_theme_mtime
from .widgets import GoalsListWidget, WorkspaceListWidget


class GoalsApp(App):
    """Super clean, minimal 2-pane goal & workspace manager following Omarchy themes."""

    CSS = generate_css(load_theme())

    BINDINGS = [
        Binding("tab", "toggle_pane", "Switch Pane", show=False),
        Binding("space", "toggle_done", "Toggle Done"),
        Binding("enter", "on_enter", "Open / Select", show=False),
        Binding("escape", "on_escape", "Back", show=False),
        Binding("n", "new_item", "New Goal"),
        Binding("a", "new_item", "Add Goal", show=False),
        Binding("e", "edit_item", "Edit"),
        Binding("d", "press_d", "Delete (dd)"),
        Binding("delete", "delete_item", "Delete", show=False),
        Binding("shift+up", "move_item_up", "Move Up", show=False),
        Binding("shift+down", "move_item_down", "Move Down", show=False),
        Binding("K", "move_item_up", "Move Up", show=False),
        Binding("J", "move_item_down", "Move Down", show=False),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.omarchy = load_theme()
        self.last_theme_mtime = get_theme_mtime()
        self.last_d_time: float = 0.0
        self.storage = Storage()
        self.goals: List[Goal] = []
        self.active_goal_idx: int = 0
        self.editing_mode: Optional[str] = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="top-bar"):
            yield Static("goals", id="top-brand")

        with Horizontal(id="main-container"):
            with Vertical(id="goals-pane"):
                yield Label("MAJOR GOALS", classes="pane-header", id="goals-header")
                yield GoalsListWidget(id="goals-list")
                yield Input(placeholder="+ New Major Goal... (Enter to save, Esc)", classes="inline-input", id="goals-input")

            with Vertical(id="workspace-pane"):
                yield Label("WORKSPACE", classes="pane-header", id="workspace-header")
                yield WorkspaceListWidget(id="workspace-list")
                yield Input(placeholder="+ New short-term goal... (Enter to save, Esc)", classes="inline-input", id="workspace-input")

        yield Static(
            "↑↓ Select  •  Shift+↑↓ Move  •  Enter Open  •  Space Done  •  n New  •  e Edit  •  dd Delete  •  Esc Back  •  q Quit",
            id="bottom-bar",
        )

    def on_mount(self) -> None:
        self.goals = self.storage.load()
        if not self.goals:
            self.goals = [Goal(title="Main Goal", items=[])]

        self.apply_theme()
        self.refresh_goals_list()
        self.refresh_workspace_list()

        # Watch for live Omarchy theme changes every 500ms
        self.set_interval(0.5, self.check_theme_update)

        # Start focused on goals list
        self.query_one("#goals-list", GoalsListWidget).focus()

    def check_theme_update(self) -> None:
        """Poll theme file mtime and update live if changed."""
        current_mtime = get_theme_mtime()
        if current_mtime != self.last_theme_mtime:
            self.last_theme_mtime = current_mtime
            self.apply_theme()

    def apply_theme(self) -> None:
        """Apply active Omarchy theme colors across all widgets dynamically."""
        theme = load_theme()
        self.omarchy = theme

        bg = theme["background"]
        dark_bg = theme["dark_background"]
        lighter_bg = theme["lighter_background"]
        fg = theme["foreground"]
        muted = theme["muted"]
        accent = theme["accent"]

        self.screen.styles.background = bg
        self.screen.styles.color = fg

        try:
            self.query_one("#top-bar").styles.background = "transparent"
            self.query_one("#top-bar").styles.color = muted
            self.query_one("#top-brand").styles.color = accent

            self.query_one("#goals-pane").styles.background = bg
            self.query_one("#workspace-pane").styles.background = bg

            self.query_one("#goals-header").styles.color = muted
            self.query_one("#goals-header").styles.border_bottom = ("solid", lighter_bg)

            self.query_one("#workspace-header").styles.border_bottom = ("solid", lighter_bg)

            self.query_one("#goals-input").styles.background = bg
            self.query_one("#goals-input").styles.border = ("tall", accent)
            self.query_one("#goals-input").styles.color = fg

            self.query_one("#workspace-input").styles.background = bg
            self.query_one("#workspace-input").styles.border = ("tall", accent)
            self.query_one("#workspace-input").styles.color = fg

            self.query_one("#bottom-bar").styles.background = "transparent"
            self.query_one("#bottom-bar").styles.color = muted

            self.update_pane_borders()
            self.refresh_goals_list()
            self.refresh_workspace_list()
        except Exception:
            pass

    def update_pane_borders(self) -> None:
        """Highlight active pane with Omarchy accent color."""
        try:
            g_pane = self.query_one("#goals-pane")
            w_pane = self.query_one("#workspace-pane")
            accent = self.omarchy["accent"]
            lighter_bg = self.omarchy["lighter_background"]

            if g_pane.has_focus_within:
                g_pane.styles.border = ("solid", accent)
                w_pane.styles.border = ("solid", lighter_bg)
            else:
                w_pane.styles.border = ("solid", accent)
                g_pane.styles.border = ("solid", lighter_bg)
        except Exception:
            pass

    def on_descendant_focus(self, event: DescendantFocus) -> None:
        self.update_pane_borders()

    def get_current_goal(self) -> Optional[Goal]:
        if 0 <= self.active_goal_idx < len(self.goals):
            return self.goals[self.active_goal_idx]
        return None

    def refresh_goals_list(self) -> None:
        g_list = self.query_one("#goals-list", GoalsListWidget)
        old_highlighted = g_list.highlighted
        g_list.clear_options()

        accent = self.omarchy["accent"]

        for idx, g in enumerate(self.goals):
            prefix = f"[{accent}]›[/] " if idx == self.active_goal_idx else "  "
            line = f"{prefix}[bold]{escape(g.title)}[/]"
            g_list.add_option(Option(line, id=g.id))

        if old_highlighted is not None and old_highlighted < len(self.goals):
            g_list.highlighted = old_highlighted
        else:
            g_list.highlighted = min(self.active_goal_idx, max(0, len(self.goals) - 1))

    def refresh_workspace_list(self) -> None:
        w_list = self.query_one("#workspace-list", WorkspaceListWidget)
        header = self.query_one("#workspace-header", Label)
        old_highlighted = w_list.highlighted
        w_list.clear_options()

        current_goal = self.get_current_goal()
        if not current_goal:
            header.update("WORKSPACE")
            w_list.add_option(Option("[dim italic]No goal selected[/]", disabled=True))
            return

        accent = self.omarchy["accent"]
        green = self.omarchy["green"]
        muted = self.omarchy["muted"]

        header.update(f"[{accent}]› {escape(current_goal.title).upper()}[/]")

        if not current_goal.items:
            w_list.add_option(Option(f"[{muted} italic]No short-term goals yet. Press 'n' to add one.[/]", disabled=True))
            return

        for it in current_goal.items:
            if it.done:
                check = f"[{green}]✔[/]"
                text = f"[strike {muted}]{escape(it.text)}[/]"
            else:
                check = f"[{muted}]◻[/]"
                text = f"[bold]{escape(it.text)}[/]"
            w_list.add_option(Option(f"{check}  {text}", id=it.id))

        if old_highlighted is not None and old_highlighted < len(current_goal.items):
            w_list.highlighted = old_highlighted
        else:
            w_list.highlighted = 0

    # Navigation events
    def on_option_list_option_highlighted(self, event: GoalsListWidget.OptionHighlighted) -> None:
        if event.option_list.id == "goals-list":
            if event.option_list.highlighted is not None:
                self.active_goal_idx = event.option_list.highlighted
                self.refresh_workspace_list()

    def on_option_list_option_selected(self, event: GoalsListWidget.OptionSelected) -> None:
        if event.option_list.id == "goals-list":
            self.action_enter_workspace()
        elif event.option_list.id == "workspace-list":
            self.action_toggle_done()

    # Actions
    def action_enter_workspace(self) -> None:
        """Step into the workspace of the active goal."""
        w_list = self.query_one("#workspace-list", WorkspaceListWidget)
        w_list.focus()
        if w_list.option_count > 0:
            w_list.highlighted = 0
        self.update_pane_borders()

    def action_exit_workspace(self) -> None:
        """Step back out to major goals."""
        if self.editing_mode:
            self._close_inline_input()
            return
        g_list = self.query_one("#goals-list", GoalsListWidget)
        g_list.focus()
        self.update_pane_borders()

    def action_toggle_pane(self) -> None:
        g_list = self.query_one("#goals-list", GoalsListWidget)
        w_list = self.query_one("#workspace-list", WorkspaceListWidget)
        if g_list.has_focus:
            self.action_enter_workspace()
        else:
            self.action_exit_workspace()

    def action_on_enter(self) -> None:
        g_list = self.query_one("#goals-list", GoalsListWidget)
        if g_list.has_focus:
            self.action_enter_workspace()
        else:
            self.action_toggle_done()

    def action_on_escape(self) -> None:
        if self.editing_mode:
            self._close_inline_input()
        else:
            self.action_exit_workspace()

    def action_toggle_done(self) -> None:
        w_list = self.query_one("#workspace-list", WorkspaceListWidget)
        current_goal = self.get_current_goal()
        if not current_goal or not current_goal.items:
            return
        idx = w_list.highlighted
        if idx is not None and 0 <= idx < len(current_goal.items):
            current_goal.items[idx].done = not current_goal.items[idx].done
            self.storage.save(self.goals)
            self.refresh_workspace_list()
            self.refresh_goals_list()

    def action_move_item_up(self) -> None:
        """Move highlighted item up in the active pane."""
        g_list = self.query_one("#goals-list", GoalsListWidget)
        if g_list.has_focus:
            idx = self.active_goal_idx
            if idx > 0 and len(self.goals) > 1:
                self.goals[idx], self.goals[idx - 1] = self.goals[idx - 1], self.goals[idx]
                self.active_goal_idx = idx - 1
                self.storage.save(self.goals)
                self.refresh_goals_list()
                g_list.highlighted = idx - 1
                self.refresh_workspace_list()
        else:
            current_goal = self.get_current_goal()
            if not current_goal or not current_goal.items:
                return
            w_list = self.query_one("#workspace-list", WorkspaceListWidget)
            idx = w_list.highlighted
            if idx is not None and idx > 0:
                current_goal.items[idx], current_goal.items[idx - 1] = current_goal.items[idx - 1], current_goal.items[idx]
                self.storage.save(self.goals)
                self.refresh_workspace_list()
                w_list.highlighted = idx - 1

    def action_move_item_down(self) -> None:
        """Move highlighted item down in the active pane."""
        g_list = self.query_one("#goals-list", GoalsListWidget)
        if g_list.has_focus:
            idx = self.active_goal_idx
            if idx < len(self.goals) - 1 and len(self.goals) > 1:
                self.goals[idx], self.goals[idx + 1] = self.goals[idx + 1], self.goals[idx]
                self.active_goal_idx = idx + 1
                self.storage.save(self.goals)
                self.refresh_goals_list()
                g_list.highlighted = idx + 1
                self.refresh_workspace_list()
        else:
            current_goal = self.get_current_goal()
            if not current_goal or not current_goal.items:
                return
            w_list = self.query_one("#workspace-list", WorkspaceListWidget)
            idx = w_list.highlighted
            if idx is not None and idx < len(current_goal.items) - 1:
                current_goal.items[idx], current_goal.items[idx + 1] = current_goal.items[idx + 1], current_goal.items[idx]
                self.storage.save(self.goals)
                self.refresh_workspace_list()
                w_list.highlighted = idx + 1

    def action_new_item(self) -> None:
        g_list = self.query_one("#goals-list", GoalsListWidget)
        if g_list.has_focus:
            self.editing_mode = "new_goal"
            inp = self.query_one("#goals-input", Input)
            inp.value = ""
            inp.placeholder = "+ Add Major Goal... (Enter to save, Esc to cancel)"
            inp.add_class("active")
            inp.focus()
        else:
            self.editing_mode = "new_item"
            inp = self.query_one("#workspace-input", Input)
            inp.value = ""
            inp.placeholder = "+ Add short-term goal... (Enter to save, Esc to cancel)"
            inp.add_class("active")
            inp.focus()

    def action_edit_item(self) -> None:
        g_list = self.query_one("#goals-list", GoalsListWidget)
        if g_list.has_focus:
            current_goal = self.get_current_goal()
            if not current_goal:
                return
            self.editing_mode = "edit_goal"
            inp = self.query_one("#goals-input", Input)
            inp.value = current_goal.title
            inp.placeholder = "Rename Major Goal..."
            inp.add_class("active")
            inp.focus()
        else:
            current_goal = self.get_current_goal()
            if not current_goal or not current_goal.items:
                return
            w_list = self.query_one("#workspace-list", WorkspaceListWidget)
            idx = w_list.highlighted
            if idx is not None and 0 <= idx < len(current_goal.items):
                self.editing_mode = "edit_item"
                inp = self.query_one("#workspace-input", Input)
                inp.value = current_goal.items[idx].text
                inp.placeholder = "Edit short-term goal..."
                inp.add_class("active")
                inp.focus()

    def action_press_d(self) -> None:
        """Require pressing 'd' twice quickly ('dd') to delete."""
        now = time.time()
        if now - self.last_d_time < 0.5:
            self.last_d_time = 0.0
            self.action_delete_item()
        else:
            self.last_d_time = now

    def action_delete_item(self) -> None:
        g_list = self.query_one("#goals-list", GoalsListWidget)
        if g_list.has_focus:
            if not self.goals:
                return
            self.goals.pop(self.active_goal_idx)
            if not self.goals:
                self.goals = [Goal(title="New Goal", items=[])]
            self.active_goal_idx = min(self.active_goal_idx, len(self.goals) - 1)
            self.storage.save(self.goals)
            self.refresh_goals_list()
            self.refresh_workspace_list()
        else:
            current_goal = self.get_current_goal()
            if not current_goal or not current_goal.items:
                return
            w_list = self.query_one("#workspace-list", WorkspaceListWidget)
            idx = w_list.highlighted
            if idx is not None and 0 <= idx < len(current_goal.items):
                current_goal.items.pop(idx)
                self.storage.save(self.goals)
                self.refresh_workspace_list()
                self.refresh_goals_list()
                if current_goal.items:
                    w_list.highlighted = min(idx, len(current_goal.items) - 1)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.value.strip()
        if not val:
            self._close_inline_input()
            return

        if self.editing_mode == "new_goal":
            new_g = Goal(title=val)
            self.goals.append(new_g)
            self.active_goal_idx = len(self.goals) - 1
            self.storage.save(self.goals)
            self.refresh_goals_list()
            self.refresh_workspace_list()
            self._close_inline_input()
            self.action_enter_workspace()

        elif self.editing_mode == "edit_goal":
            current_goal = self.get_current_goal()
            if current_goal:
                current_goal.title = val
                self.storage.save(self.goals)
                self.refresh_goals_list()
                self.refresh_workspace_list()
            self._close_inline_input()

        elif self.editing_mode == "new_item":
            current_goal = self.get_current_goal()
            if current_goal:
                current_goal.items.append(GoalItem(text=val))
                self.storage.save(self.goals)
                self.refresh_workspace_list()
                self.refresh_goals_list()
                event.input.value = ""

        elif self.editing_mode == "edit_item":
            current_goal = self.get_current_goal()
            w_list = self.query_one("#workspace-list", WorkspaceListWidget)
            idx = w_list.highlighted
            if current_goal and idx is not None and 0 <= idx < len(current_goal.items):
                current_goal.items[idx].text = val
                self.storage.save(self.goals)
                self.refresh_workspace_list()
            self._close_inline_input()

    def _close_inline_input(self) -> None:
        goals_inp = self.query_one("#goals-input", Input)
        ws_inp = self.query_one("#workspace-input", Input)
        goals_inp.remove_class("active")
        ws_inp.remove_class("active")

        mode = self.editing_mode
        self.editing_mode = None

        if mode in ("new_goal", "edit_goal"):
            self.query_one("#goals-list", GoalsListWidget).focus()
        else:
            self.query_one("#workspace-list", WorkspaceListWidget).focus()
        self.update_pane_borders()

    def action_quit_app(self) -> None:
        self.exit()
