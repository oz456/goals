from typing import List, Optional, Tuple
from datetime import date
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, Label
from textual.widgets.option_list import Option
from rich.markup import escape

from ..models import Project, Task, Priority
from ..storage import Storage
from ..date_utils import format_due_date_badge
from .widgets import ProjectListWidget, TaskListWidget
from .screens import (
    TaskModal,
    ProjectModal,
    QuickDueDateModal,
    SubtaskModal,
    ConfirmModal,
    HelpModal,
)


class WorkApp(App):
    """Work - Intuitive dual-pane project & task manager."""

    CSS = """
    Screen {
        background: #181825;
        color: #cdd6f4;
    }

    #app-header {
        height: 3;
        dock: top;
        background: #1e1e2e;
        border-bottom: heavy #313244;
        padding: 0 2;
        content-align: center middle;
    }

    #header-brand {
        width: 1fr;
        text-style: bold;
    }

    #header-stats {
        width: auto;
        color: #a6e3a1;
        text-style: bold;
    }

    #search-container {
        height: 3;
        dock: top;
        background: #1e1e2e;
        padding: 0 1;
        display: none;
    }

    #search-container.visible {
        display: block;
    }

    #filter-input {
        width: 100%;
        border: tall #89b4fa;
        background: #313244;
    }

    #main-container {
        height: 1fr;
    }

    #projects-pane {
        width: 32%;
        height: 100%;
        border: round #313244;
        background: #181825;
        padding: 0 1;
    }

    #projects-pane:focus-within {
        border: round #89b4fa;
    }

    #tasks-pane {
        width: 68%;
        height: 100%;
        border: round #313244;
        background: #181825;
        padding: 0 1;
    }

    #tasks-pane:focus-within {
        border: round #89b4fa;
    }

    .pane-title {
        height: 1;
        margin: 1 0 0 1;
        text-style: bold;
        color: #89b4fa;
    }

    #projects-list {
        height: 1fr;
        background: transparent;
        border: none;
    }

    #tasks-list {
        height: 1fr;
        background: transparent;
        border: none;
    }

    Footer {
        background: #1e1e2e;
        color: #a6adc8;
    }
    """

    BINDINGS = [
        Binding("tab", "toggle_pane", "Switch Pane"),
        Binding("space", "toggle_complete", "Toggle Done"),
        Binding("n", "add_item", "New"),
        Binding("a", "add_item", "Add", show=False),
        Binding("e", "edit_item", "Edit"),
        Binding("enter", "on_enter", "Select / Edit", show=False),
        Binding("d", "delete_item", "Delete"),
        Binding("delete", "delete_item", "Delete", show=False),
        Binding("1", "set_priority_high", "High Priority", show=False),
        Binding("2", "set_priority_med", "Med Priority", show=False),
        Binding("3", "set_priority_low", "Low Priority", show=False),
        Binding("4", "set_priority_none", "No Priority", show=False),
        Binding("p", "cycle_priority", "Priority"),
        Binding("t", "set_due_date", "Due Date"),
        Binding("s", "manage_subtasks", "Subtasks"),
        Binding("slash", "open_search", "Filter"),
        Binding("escape", "clear_search", "Clear Filter", show=False),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.storage = Storage()
        self.projects: List[Project] = []
        self.tasks: List[Task] = []
        self.active_view: str = "inbox"  # Smart view or project_id
        self.filter_query: str = ""
        self.displayed_tasks: List[Task] = []

    def compose(self) -> ComposeResult:
        with Horizontal(id="app-header"):
            yield Static("[bold #cba6f7]WORK[/] [dim]• focused task manager[/]", id="header-brand")
            yield Static("0 / 0 Done", id="header-stats")

        with Container(id="search-container"):
            yield Input(placeholder="🔍 Type to filter tasks... (Esc to cancel, Enter to jump to list)", id="filter-input")

        with Horizontal(id="main-container"):
            with Vertical(id="projects-pane"):
                yield Label("PROJECTS", classes="pane-title")
                yield ProjectListWidget(id="projects-list")

            with Vertical(id="tasks-pane"):
                yield Label("TASKS", id="tasks-pane-title", classes="pane-title")
                yield TaskListWidget(id="tasks-list")

        yield Footer()

    def on_mount(self) -> None:
        self.projects, self.tasks = self.storage.load()
        if not self.projects:
            self.projects = [Project(id="inbox", name="Inbox", icon="📥")]

        self.refresh_projects_list()
        self.refresh_tasks_list()
        self.update_header_stats()

        # Initial focus on tasks pane
        self.query_one("#tasks-list", TaskListWidget).focus()

    def update_header_stats(self) -> None:
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        pct = int((completed / total) * 100) if total > 0 else 0
        stats_widget = self.query_one("#header-stats", Static)
        stats_widget.update(f"[bold #a6e3a1]✔ {completed}/{total} Done ({pct}%)[/]")

    def refresh_projects_list(self) -> None:
        p_list = self.query_one("#projects-list", ProjectListWidget)
        old_highlighted = p_list.highlighted
        p_list.clear_options()

        today = date.today()
        all_pending = sum(1 for t in self.tasks if not t.completed)
        today_count = sum(1 for t in self.tasks if not t.completed and t.due_date and date.fromisoformat(t.due_date) <= today)
        high_count = sum(1 for t in self.tasks if not t.completed and t.priority == Priority.HIGH)
        done_count = sum(1 for t in self.tasks if t.completed)

        # Smart Views
        p_list.add_option(Option(f"📋 All Tasks [dim]({all_pending})[/]", id="__all__"))
        p_list.add_option(Option(f"⭐ Today & Overdue [dim]({today_count})[/]", id="__today__"))
        p_list.add_option(Option(f"🔥 High Priority [dim]({high_count})[/]", id="__high__"))
        p_list.add_option(Option(f"✔ Completed [dim]({done_count})[/]", id="__completed__"))
        p_list.add_option(Option("[dim]─────────────────────[/]", disabled=True, id="__sep__"))

        # User Projects
        for p in self.projects:
            count = sum(1 for t in self.tasks if t.project_id == p.id and not t.completed)
            safe_name = escape(p.name)
            p_list.add_option(Option(f"{p.icon}  {safe_name} [dim]({count})[/]", id=p.id))

        # Restore highlight
        target_idx = 0
        for idx in range(p_list.option_count):
            opt = p_list.get_option_at_index(idx)
            if opt and opt.id == self.active_view:
                target_idx = idx
                break
        p_list.highlighted = target_idx

    def get_current_project(self) -> Optional[Project]:
        for p in self.projects:
            if p.id == self.active_view:
                return p
        return None

    def refresh_tasks_list(self) -> None:
        t_list = self.query_one("#tasks-list", TaskListWidget)
        title_label = self.query_one("#tasks-pane-title", Label)
        old_highlighted = t_list.highlighted
        t_list.clear_options()

        today = date.today()

        # Filter by active view
        if self.active_view == "__all__":
            title_label.update("📋 ALL TASKS")
            filtered = list(self.tasks)
        elif self.active_view == "__today__":
            title_label.update("⭐ TODAY & OVERDUE")
            filtered = [
                t for t in self.tasks
                if not t.completed and t.due_date and date.fromisoformat(t.due_date) <= today
            ]
        elif self.active_view == "__high__":
            title_label.update("🔥 HIGH PRIORITY")
            filtered = [t for t in self.tasks if not t.completed and t.priority == Priority.HIGH]
        elif self.active_view == "__completed__":
            title_label.update("✔ COMPLETED TASKS")
            filtered = [t for t in self.tasks if t.completed]
        else:
            proj = self.get_current_project()
            name = proj.name if proj else "Inbox"
            icon = proj.icon if proj else "📁"
            title_label.update(f"{icon}  {name.upper()}")
            filtered = [t for t in self.tasks if t.project_id == self.active_view]

        # Apply search filter if any
        if self.filter_query:
            q = self.filter_query.lower()
            filtered = [t for t in filtered if q in t.title.lower() or (t.notes and q in t.notes.lower())]

        # Smart sort: uncompleted first, then by priority (descending), then by due date
        def sort_key(task: Task):
            is_done = 1 if task.completed else 0
            pri = -int(task.priority)
            due_str = task.due_date or "9999-99-99"
            return (is_done, pri, due_str)

        filtered.sort(key=sort_key)
        self.displayed_tasks = filtered

        if not filtered:
            msg = "[dim italic]No tasks found here. Press [b]n[/b] to add one![/]"
            if self.filter_query:
                safe_q = escape(self.filter_query)
                msg = f"[dim italic]No tasks matching '{safe_q}'[/]"
            t_list.add_option(Option(msg, id="__empty__", disabled=True))
            return

        for t in filtered:
            # Checkbox
            check = "[bold #a6e3a1]✔[/]" if t.completed else "[dim]◻[/]"

            # Title formatting
            safe_title = escape(t.title)
            title_text = f"[strike dim]{safe_title}[/]" if t.completed else f"[bold]{safe_title}[/]"

            # Priority
            pri_badge = f" {t.priority.badge}" if t.priority != Priority.NONE else ""

            # Due date badge
            due_badge = ""
            if t.due_date:
                badge_text, color = format_due_date_badge(t.due_date)
                due_badge = f" [{color}]{badge_text}[/]"

            # Subtasks badge
            sub_badge = ""
            if t.subtasks:
                sub_done = sum(1 for s in t.subtasks if s.completed)
                sub_total = len(t.subtasks)
                sub_badge = f" [cyan]\\[{sub_done}/{sub_total}][/]"

            full_line = f"{check}  {title_text}{pri_badge}{due_badge}{sub_badge}"
            t_list.add_option(Option(full_line, id=t.id))

        if old_highlighted is not None and old_highlighted < len(filtered):
            t_list.highlighted = old_highlighted
        else:
            t_list.highlighted = 0

    def get_highlighted_task(self) -> Optional[Task]:
        t_list = self.query_one("#tasks-list", TaskListWidget)
        if t_list.highlighted is None or not self.displayed_tasks:
            return None
        idx = t_list.highlighted
        if 0 <= idx < len(self.displayed_tasks):
            return self.displayed_tasks[idx]
        return None

    # Focus navigation
    def action_focus_projects(self) -> None:
        self.query_one("#projects-list", ProjectListWidget).focus()

    def action_focus_tasks(self) -> None:
        self.query_one("#tasks-list", TaskListWidget).focus()

    def action_toggle_pane(self) -> None:
        p_list = self.query_one("#projects-list", ProjectListWidget)
        t_list = self.query_one("#tasks-list", TaskListWidget)
        if p_list.has_focus:
            t_list.focus()
        else:
            p_list.focus()

    # Events from lists
    def on_option_list_option_highlighted(self, event: ProjectListWidget.OptionHighlighted) -> None:
        if event.option_list.id == "projects-list":
            if event.option and event.option.id and not event.option.id.startswith("__sep__"):
                self.active_view = event.option.id
                self.refresh_tasks_list()

    def on_option_list_option_selected(self, event: TaskListWidget.OptionSelected) -> None:
        if event.option_list.id == "projects-list":
            self.action_focus_tasks()
        elif event.option_list.id == "tasks-list":
            self.action_edit_item()

    # Task & Project Actions
    def action_toggle_complete(self) -> None:
        task = self.get_highlighted_task()
        if not task:
            return
        task.completed = not task.completed
        self.storage.save(self.projects, self.tasks)
        self.refresh_tasks_list()
        self.refresh_projects_list()
        self.update_header_stats()

    def action_add_item(self) -> None:
        p_list = self.query_one("#projects-list", ProjectListWidget)
        if p_list.has_focus:
            self.push_screen(ProjectModal(title="Create New Project"), self._on_project_created)
        else:
            default_proj = "inbox"
            if not self.active_view.startswith("__"):
                default_proj = self.active_view
            elif self.projects:
                default_proj = self.projects[0].id

            self.push_screen(
                TaskModal(project_id=default_proj, title="Create New Task"),
                self._on_task_created,
            )

    def _on_project_created(self, result: Optional[dict]) -> None:
        if not result:
            return
        new_proj = Project(name=result["name"], icon=result["icon"])
        self.projects.append(new_proj)
        self.storage.save(self.projects, self.tasks)
        self.active_view = new_proj.id
        self.refresh_projects_list()
        self.refresh_tasks_list()
        self.notify(f"Created project '{new_proj.name}'")

    def _on_task_created(self, result: Optional[dict]) -> None:
        if not result:
            return
        new_task = Task(
            title=result["title"],
            project_id=result["project_id"],
            priority=result["priority"],
            due_date=result["due_date"],
        )
        self.tasks.append(new_task)
        self.storage.save(self.projects, self.tasks)
        self.refresh_tasks_list()
        self.refresh_projects_list()
        self.update_header_stats()
        self.notify(f"Added task '{new_task.title}'")

    def action_on_enter(self) -> None:
        p_list = self.query_one("#projects-list", ProjectListWidget)
        if p_list.has_focus:
            self.action_focus_tasks()
        else:
            self.action_edit_item()

    def action_edit_item(self) -> None:
        p_list = self.query_one("#projects-list", ProjectListWidget)
        if p_list.has_focus:
            proj = self.get_current_project()
            if not proj:
                self.notify("Smart views cannot be edited", severity="warning")
                return
            self.push_screen(
                ProjectModal(project=proj, title=f"Rename Project '{proj.name}'"),
                lambda res: self._on_project_edited(proj, res),
            )
        else:
            task = self.get_highlighted_task()
            if not task:
                return
            self.push_screen(
                TaskModal(task=task, project_id=task.project_id, title="Edit Task"),
                lambda res: self._on_task_edited(task, res),
            )

    def _on_project_edited(self, proj: Project, result: Optional[dict]) -> None:
        if not result:
            return
        proj.name = result["name"]
        proj.icon = result["icon"]
        self.storage.save(self.projects, self.tasks)
        self.refresh_projects_list()
        self.refresh_tasks_list()

    def _on_task_edited(self, task: Task, result: Optional[dict]) -> None:
        if not result:
            return
        task.title = result["title"]
        task.priority = result["priority"]
        task.due_date = result["due_date"]
        self.storage.save(self.projects, self.tasks)
        self.refresh_tasks_list()
        self.refresh_projects_list()

    def action_delete_item(self) -> None:
        p_list = self.query_one("#projects-list", ProjectListWidget)
        if p_list.has_focus:
            proj = self.get_current_project()
            if not proj:
                self.notify("Smart views cannot be deleted", severity="warning")
                return
            count = sum(1 for t in self.tasks if t.project_id == proj.id)
            msg = f"Delete project '{proj.name}' and its {count} tasks?"
            self.push_screen(ConfirmModal(msg), lambda confirmed: self._on_project_deleted(proj, confirmed))
        else:
            task = self.get_highlighted_task()
            if not task:
                return
            self.push_screen(
                ConfirmModal(f"Delete task '{task.title}'?"),
                lambda confirmed: self._on_task_deleted(task, confirmed),
            )

    def _on_project_deleted(self, proj: Project, confirmed: bool) -> None:
        if not confirmed:
            return
        self.projects = [p for p in self.projects if p.id != proj.id]
        self.tasks = [t for t in self.tasks if t.project_id != proj.id]
        self.storage.save(self.projects, self.tasks)
        self.active_view = "inbox" if self.projects else "__all__"
        self.refresh_projects_list()
        self.refresh_tasks_list()
        self.update_header_stats()
        self.notify(f"Deleted project '{proj.name}'")

    def _on_task_deleted(self, task: Task, confirmed: bool) -> None:
        if not confirmed:
            return
        self.tasks = [t for t in self.tasks if t.id != task.id]
        self.storage.save(self.projects, self.tasks)
        self.refresh_tasks_list()
        self.refresh_projects_list()
        self.update_header_stats()
        self.notify(f"Deleted '{task.title}'")

    # Priority controls
    def action_set_priority_high(self) -> None:
        self._set_priority(Priority.HIGH)

    def action_set_priority_med(self) -> None:
        self._set_priority(Priority.MEDIUM)

    def action_set_priority_low(self) -> None:
        self._set_priority(Priority.LOW)

    def action_set_priority_none(self) -> None:
        self._set_priority(Priority.NONE)

    def action_cycle_priority(self) -> None:
        task = self.get_highlighted_task()
        if not task:
            return
        next_pri = {
            Priority.NONE: Priority.LOW,
            Priority.LOW: Priority.MEDIUM,
            Priority.MEDIUM: Priority.HIGH,
            Priority.HIGH: Priority.NONE,
        }[task.priority]
        self._set_priority(next_pri)

    def _set_priority(self, priority: Priority) -> None:
        task = self.get_highlighted_task()
        if not task:
            return
        task.priority = priority
        self.storage.save(self.projects, self.tasks)
        self.refresh_tasks_list()
        self.refresh_projects_list()

    # Due date
    def action_set_due_date(self) -> None:
        task = self.get_highlighted_task()
        if not task:
            return
        self.push_screen(
            QuickDueDateModal(task.due_date),
            lambda new_due: self._on_due_date_set(task, new_due),
        )

    def _on_due_date_set(self, task: Task, new_due: Optional[str]) -> None:
        if new_due is None:
            return
        task.due_date = new_due if new_due else None
        self.storage.save(self.projects, self.tasks)
        self.refresh_tasks_list()
        self.refresh_projects_list()

    # Subtasks
    def action_manage_subtasks(self) -> None:
        task = self.get_highlighted_task()
        if not task:
            return
        self.push_screen(
            SubtaskModal(task),
            lambda subtasks: self._on_subtasks_updated(task, subtasks),
        )

    def _on_subtasks_updated(self, task: Task, subtasks: List) -> None:
        task.subtasks = subtasks
        self.storage.save(self.projects, self.tasks)
        self.refresh_tasks_list()

    # Filter / Search
    def action_open_search(self) -> None:
        search_box = self.query_one("#search-container", Container)
        search_box.add_class("visible")
        inp = self.query_one("#filter-input", Input)
        inp.focus()

    def action_clear_search(self) -> None:
        search_box = self.query_one("#search-container", Container)
        inp = self.query_one("#filter-input", Input)
        inp.value = ""
        self.filter_query = ""
        search_box.remove_class("visible")
        self.refresh_tasks_list()
        self.action_focus_tasks()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "filter-input":
            self.filter_query = event.value.strip()
            self.refresh_tasks_list()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "filter-input":
            self.action_focus_tasks()

    # Help & Quit
    def action_show_help(self) -> None:
        self.push_screen(HelpModal())

    def action_quit_app(self) -> None:
        self.exit()
