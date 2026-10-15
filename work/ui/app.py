from typing import List, Optional
from rich.markup import escape
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, Label
from textual.widgets.option_list import Option

from ..models import Goal, GoalItem
from ..storage import Storage
from ..theme import load_theme, generate_css
from .widgets import GoalsListWidget, WorkspaceListWidget


class WorkApp(App):
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
        Binding("d", "delete_item", "Delete"),
        Binding("delete", "delete_item", "Delete", show=False),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.omarchy = load_theme()
        self.storage = Storage()
        self.goals: List[Goal] = []
        self.active_goal_idx: int = 0
        self.editing_mode: Optional[str] = None  # None, "new_goal", "edit_goal", "new_item", "edit_item"

    def compose(self) -> ComposeResult:
        with Horizontal(id="top-bar"):
            yield Static("toru", id="top-brand")
            yield Static("0/0 done", id="top-stats")

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
            "↑↓ Move  •  Enter Open Workspace  •  Space Done  •  n New  •  e Edit  •  d Delete  •  Esc Back  •  q Quit",
            id="bottom-bar",
        )

    def on_mount(self) -> None:
        self.goals = self.storage.load()
        if not self.goals:
            self.goals = [Goal(title="Main Goal", items=[])]

        self.refresh_goals_list()
        self.refresh_workspace_list()
        self.update_stats()

        # Start focused on goals list
        self.query_one("#goals-list", GoalsListWidget).focus()

    def get_current_goal(self) -> Optional[Goal]:
        if 0 <= self.active_goal_idx < len(self.goals):
            return self.goals[self.active_goal_idx]
        return None

    def update_stats(self) -> None:
        total = sum(len(g.items) for g in self.goals)
        completed = sum(sum(1 for it in g.items if it.done) for g in self.goals)
        top_stats = self.query_one("#top-stats", Static)
        top_stats.update(f"{completed}/{total} done")

    def refresh_goals_list(self) -> None:
        g_list = self.query_one("#goals-list", GoalsListWidget)
        old_highlighted = g_list.highlighted
        g_list.clear_options()

        accent = self.omarchy["accent"]
        muted = self.omarchy["muted"]

        for idx, g in enumerate(self.goals):
            done_count = sum(1 for it in g.items if it.done)
            total_count = len(g.items)
            counter = f"[{muted}]({done_count}/{total_count})[/]" if total_count > 0 else ""
            prefix = "› " if idx == self.active_goal_idx else "  "
            line = f"{prefix}[bold]{escape(g.title)}[/] {counter}"
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
            w_list.add_option(Option("[dim italic]No short-term goals yet. Press [b]n[/b] to add one.[/]", disabled=True))
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

    def action_exit_workspace(self) -> None:
        """Step back out to major goals."""
        if self.editing_mode:
            self._close_inline_input()
            return
        g_list = self.query_one("#goals-list", GoalsListWidget)
        g_list.focus()

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
            self.update_stats()

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
            self.update_stats()
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
                self.update_stats()
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
            self.update_stats()
            self._close_inline_input()
            # Jump straight into the new goal's workspace!
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
                self.update_stats()
                event.input.value = ""
                # Keep input open to type next item quickly!

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

    def action_quit_app(self) -> None:
        self.exit()
