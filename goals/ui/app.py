import time
from typing import List, Optional, Any
from rich.markup import escape
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Input, Label
from textual.widgets.option_list import Option
from textual.events import DescendantFocus

from ..models import Workspace, Goal, GoalItem
from ..storage import Storage
from ..theme import load_theme, generate_css, get_theme_mtime
from .widgets import GoalsListWidget, WorkspaceListWidget, HelpScreen


class GoalsApp(App):
    """Super clean, minimal multi-window 2-pane goal manager following Omarchy themes."""

    CSS = generate_css(load_theme())

    BINDINGS = [
        # Navigation & Panes
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
        Binding("question_mark", "show_help", "Help"),
        Binding("?", "show_help", "Help", show=False),
        Binding("f1", "show_help", "Help", show=False),
        Binding("q", "quit_app", "Quit"),

        # Multi-window / Workspace Tabs (Herdr conventions)
        Binding("alt+1", "tab_1", "Tab 1", show=False),
        Binding("alt+2", "tab_2", "Tab 2", show=False),
        Binding("alt+3", "tab_3", "Tab 3", show=False),
        Binding("alt+4", "tab_4", "Tab 4", show=False),
        Binding("alt+5", "tab_5", "Tab 5", show=False),
        Binding("alt+6", "tab_6", "Tab 6", show=False),
        Binding("alt+7", "tab_7", "Tab 7", show=False),
        Binding("alt+8", "tab_8", "Tab 8", show=False),
        Binding("alt+9", "tab_9", "Tab 9", show=False),
        Binding("alt+left", "prev_tab", "Prev Tab", show=False),
        Binding("alt+right", "next_tab", "Next Tab", show=False),
        Binding("[", "prev_tab", "Prev Tab", show=False),
        Binding("]", "next_tab", "Next Tab", show=False),
        Binding("alt+shift+left", "move_tab_left", "Move Tab Left", show=False),
        Binding("alt+shift+right", "move_tab_right", "Move Tab Right", show=False),
        Binding("alt+H", "move_tab_left", "Move Tab Left", show=False),
        Binding("alt+L", "move_tab_right", "Move Tab Right", show=False),
        Binding("{", "move_tab_left", "Move Tab Left", show=False),
        Binding("}", "move_tab_right", "Move Tab Right", show=False),
        Binding("alt+t", "new_tab", "New Window"),
        Binding("ctrl+t", "new_tab", "New Window", show=False),
        Binding("alt+r", "rename_tab", "Rename Window"),
        Binding("ctrl+r", "rename_tab", "Rename Window", show=False),
        Binding("alt+w", "close_tab", "Close Window"),
        Binding("ctrl+w", "close_tab", "Close Window", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.omarchy = load_theme()
        self.last_theme_mtime = get_theme_mtime()
        self.last_d_time: float = 0.0
        self.storage = Storage()
        self.workspaces: List[Workspace] = []
        self.active_ws_idx: int = 0
        self.active_goal_idx: int = 0
        self.editing_mode: Optional[str] = None

    @property
    def current_workspace(self) -> Workspace:
        if not self.workspaces:
            self.workspaces = [Workspace(title="Main", goals=[])]
        if self.active_ws_idx >= len(self.workspaces):
            self.active_ws_idx = max(0, len(self.workspaces) - 1)
        return self.workspaces[self.active_ws_idx]

    @property
    def goals(self) -> List[Goal]:
        return self.current_workspace.goals

    @goals.setter
    def goals(self, value: List[Goal]) -> None:
        self.current_workspace.goals = value

    def save_data(self) -> None:
        self.storage.save(self.workspaces)

    def compose(self) -> ComposeResult:
        with Horizontal(id="top-bar"):
            yield Static("", id="tabs-header")

        yield Input(placeholder="+ New Window Name... (Enter to save, Esc)", classes="inline-input", id="tab-input")

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
            "[@click=app.show_help]? Help[/]  •  ↑↓ Nav  •  Enter Open  •  Space Done  •  n New  •  q Quit",
            id="bottom-bar",
        )

    def on_mount(self) -> None:
        self.workspaces = self.storage.load()
        if not self.workspaces:
            self.workspaces = [Workspace(title="Main", goals=[])]

        self.apply_theme()
        self.refresh_tabs()
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
        lighter_bg = theme["lighter_background"]
        fg = theme["foreground"]
        muted = theme["muted"]
        accent = theme["accent"]

        self.screen.styles.background = bg
        self.screen.styles.color = fg

        try:
            self.query_one("#top-bar").styles.background = "transparent"
            self.query_one("#tabs-header").styles.background = "transparent"

            self.query_one("#tab-input").styles.background = bg
            self.query_one("#tab-input").styles.border = ("tall", accent)
            self.query_one("#tab-input").styles.color = fg

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
            self.refresh_tabs()
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

    def refresh_tabs(self) -> None:
        try:
            tabs_widget = self.query_one("#tabs-header", Static)
        except Exception:
            return

        accent = self.omarchy.get("accent", "#e63946")
        dark_bg = self.omarchy.get("dark_background", "#080808")
        selection = self.omarchy.get("selection", "#343d41")
        muted = self.omarchy.get("muted", "#5c5c5c")

        parts = []
        for idx, ws in enumerate(self.workspaces):
            title = escape(ws.title)
            if idx == self.active_ws_idx:
                # Active tab: Herdr panel_bg on accent background
                parts.append(f"[@click=app.switch_tab({idx})][bold {dark_bg} on {accent}] {title} [/][/]")
            else:
                # Inactive tab: clean muted text
                parts.append(f"[@click=app.switch_tab({idx})][{muted}] {title} [/][/]")

        # Pure Herdr style: clean names separated by vertical border divider, no index prefixes
        divider = f"[{selection}]│[/]"
        tabs_widget.update(divider.join(parts))

    def refresh_goals_list(self) -> None:
        g_list = self.query_one("#goals-list", GoalsListWidget)
        old_highlighted = g_list.highlighted
        g_list.clear_options()

        accent = self.omarchy["accent"]
        muted = self.omarchy["muted"]

        if not self.goals:
            g_list.add_option(Option(f"[{muted} italic]No major goals yet. Press 'n' to add one.[/]", disabled=True))
            return

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
            if event.option_list.highlighted is not None and event.option_list.highlighted < len(self.goals):
                self.active_goal_idx = event.option_list.highlighted
                self.refresh_workspace_list()

    def on_option_list_option_selected(self, event: GoalsListWidget.OptionSelected) -> None:
        if event.option_list.id == "goals-list":
            self.action_enter_workspace()
        elif event.option_list.id == "workspace-list":
            self.action_toggle_done()

    # Workspace Tab Actions (Herdr style)
    def action_switch_tab(self, idx: Any) -> None:
        try:
            tab_idx = int(idx)
        except (ValueError, TypeError):
            return
        if 0 <= tab_idx < len(self.workspaces):
            self.active_ws_idx = tab_idx
            self.active_goal_idx = 0
            self.refresh_tabs()
            self.refresh_goals_list()
            self.refresh_workspace_list()
            if not self.goals:
                self.query_one("#goals-list", GoalsListWidget).focus()
            self.update_pane_borders()

    def action_tab_1(self) -> None: self.action_switch_tab(0)
    def action_tab_2(self) -> None: self.action_switch_tab(1)
    def action_tab_3(self) -> None: self.action_switch_tab(2)
    def action_tab_4(self) -> None: self.action_switch_tab(3)
    def action_tab_5(self) -> None: self.action_switch_tab(4)
    def action_tab_6(self) -> None: self.action_switch_tab(5)
    def action_tab_7(self) -> None: self.action_switch_tab(6)
    def action_tab_8(self) -> None: self.action_switch_tab(7)
    def action_tab_9(self) -> None: self.action_switch_tab(8)

    def action_prev_tab(self) -> None:
        if len(self.workspaces) > 1:
            new_idx = (self.active_ws_idx - 1) % len(self.workspaces)
            self.action_switch_tab(new_idx)

    def action_next_tab(self) -> None:
        if len(self.workspaces) > 1:
            new_idx = (self.active_ws_idx + 1) % len(self.workspaces)
            self.action_switch_tab(new_idx)

    def action_move_tab_left(self) -> None:
        """Rearrange active tab leftwards."""
        if self.active_ws_idx > 0:
            idx = self.active_ws_idx
            self.workspaces[idx], self.workspaces[idx - 1] = self.workspaces[idx - 1], self.workspaces[idx]
            self.active_ws_idx = idx - 1
            self.save_data()
            self.refresh_tabs()

    def action_move_tab_right(self) -> None:
        """Rearrange active tab rightwards."""
        if self.active_ws_idx < len(self.workspaces) - 1:
            idx = self.active_ws_idx
            self.workspaces[idx], self.workspaces[idx + 1] = self.workspaces[idx + 1], self.workspaces[idx]
            self.active_ws_idx = idx + 1
            self.save_data()
            self.refresh_tabs()

    def action_new_tab(self) -> None:
        """Open inline prompt to create new window/workspace."""
        self.editing_mode = "new_tab"
        inp = self.query_one("#tab-input", Input)
        inp.value = ""
        inp.placeholder = "+ New Window Name... (Enter to save, Esc to cancel)"
        inp.add_class("active")
        inp.focus()

    def action_rename_tab(self) -> None:
        """Open inline prompt to rename active window/workspace."""
        if not self.workspaces:
            return
        self.editing_mode = "rename_tab"
        curr_ws = self.current_workspace
        inp = self.query_one("#tab-input", Input)
        inp.value = curr_ws.title
        inp.placeholder = "Rename Window... (Enter to save, Esc to cancel)"
        inp.add_class("active")
        inp.focus()

    def action_close_tab(self) -> None:
        """Close active window/workspace (keeps at least 1 window)."""
        if len(self.workspaces) <= 1:
            return
        self.workspaces.pop(self.active_ws_idx)
        self.active_ws_idx = min(self.active_ws_idx, len(self.workspaces) - 1)
        self.active_goal_idx = 0
        self.save_data()
        self.refresh_tabs()
        self.refresh_goals_list()
        self.refresh_workspace_list()
        self.query_one("#goals-list", GoalsListWidget).focus()
        self.update_pane_borders()

    # Pane Actions
    def action_enter_workspace(self) -> None:
        """Step into the workspace of the active goal."""
        current_goal = self.get_current_goal()
        if not current_goal:
            return
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
            self.save_data()
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
                self.save_data()
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
                self.save_data()
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
                self.save_data()
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
                self.save_data()
                self.refresh_workspace_list()
                w_list.highlighted = idx + 1

    def action_new_item(self) -> None:
        g_list = self.query_one("#goals-list", GoalsListWidget)
        if g_list.has_focus or not self.goals:
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
            if self.goals:
                self.active_goal_idx = min(self.active_goal_idx, len(self.goals) - 1)
            else:
                self.active_goal_idx = 0
            self.save_data()
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
                self.save_data()
                self.refresh_workspace_list()
                self.refresh_goals_list()
                if current_goal.items:
                    w_list.highlighted = min(idx, len(current_goal.items) - 1)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.value.strip()
        if not val:
            self._close_inline_input()
            return

        if self.editing_mode == "new_tab":
            title = val if val else f"Window {len(self.workspaces) + 1}"
            new_ws = Workspace(title=title, goals=[])
            self.workspaces.append(new_ws)
            self.active_ws_idx = len(self.workspaces) - 1
            self.active_goal_idx = 0
            self.save_data()
            self.refresh_tabs()
            self.refresh_goals_list()
            self.refresh_workspace_list()
            self._close_inline_input()
            self.query_one("#goals-list", GoalsListWidget).focus()

        elif self.editing_mode == "rename_tab":
            if val:
                self.current_workspace.title = val
                self.save_data()
                self.refresh_tabs()
            self._close_inline_input()

        elif self.editing_mode == "new_goal":
            new_g = Goal(title=val)
            self.goals.append(new_g)
            self.active_goal_idx = len(self.goals) - 1
            self.save_data()
            self.refresh_goals_list()
            self.refresh_workspace_list()
            self._close_inline_input()
            self.action_enter_workspace()

        elif self.editing_mode == "edit_goal":
            current_goal = self.get_current_goal()
            if current_goal:
                current_goal.title = val
                self.save_data()
                self.refresh_goals_list()
                self.refresh_workspace_list()
            self._close_inline_input()

        elif self.editing_mode == "new_item":
            current_goal = self.get_current_goal()
            if current_goal:
                current_goal.items.append(GoalItem(text=val))
                self.save_data()
                self.refresh_workspace_list()
                self.refresh_goals_list()
                event.input.value = ""

        elif self.editing_mode == "edit_item":
            current_goal = self.get_current_goal()
            w_list = self.query_one("#workspace-list", WorkspaceListWidget)
            idx = w_list.highlighted
            if current_goal and idx is not None and 0 <= idx < len(current_goal.items):
                current_goal.items[idx].text = val
                self.save_data()
                self.refresh_workspace_list()
            self._close_inline_input()

    def _close_inline_input(self) -> None:
        goals_inp = self.query_one("#goals-input", Input)
        ws_inp = self.query_one("#workspace-input", Input)
        tab_inp = self.query_one("#tab-input", Input)
        goals_inp.remove_class("active")
        ws_inp.remove_class("active")
        tab_inp.remove_class("active")

        mode = self.editing_mode
        self.editing_mode = None

        if mode in ("new_tab", "rename_tab", "new_goal", "edit_goal"):
            self.query_one("#goals-list", GoalsListWidget).focus()
        else:
            self.query_one("#workspace-list", WorkspaceListWidget).focus()
        self.update_pane_borders()

    def action_show_help(self) -> None:
        if isinstance(self.screen, HelpScreen):
            self.screen.dismiss()
        else:
            self.push_screen(HelpScreen(self.omarchy))

    def action_quit_app(self) -> None:
        self.exit()
