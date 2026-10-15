import json
import os
import tempfile
from pathlib import Path
from typing import List, Tuple
from datetime import date, timedelta

from .models import Project, Task, Subtask, Priority

DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "toru"
DEFAULT_DATA_FILE = DEFAULT_DATA_DIR / "data.json"


def get_default_seed() -> Tuple[List[Project], List[Task]]:
    """Seed data for initial launch."""
    projects = [
        Project(id="inbox", name="Inbox", icon="📥", color="#89b4fa"),
        Project(id="work", name="Work", icon="💼", color="#f9e2af"),
        Project(id="personal", name="Personal", icon="🏠", color="#a6e3a1"),
    ]

    today = date.today()
    tmr = today + timedelta(days=1)

    tasks = [
        Task(
            project_id="inbox",
            title="Welcome to Toru! Press [Space] to complete me",
            completed=False,
            priority=Priority.HIGH,
            due_date=today.isoformat(),
            subtasks=[
                Subtask(title="Try clicking this checkbox", completed=False),
                Subtask(title="Press [s] to open subtask manager", completed=True),
            ],
        ),
        Task(
            project_id="inbox",
            title="Press [Tab] or [←] / [→] to switch between Projects and Tasks",
            completed=False,
            priority=Priority.MEDIUM,
            due_date=tmr.isoformat(),
        ),
        Task(
            project_id="inbox",
            title="Arrow keys ↑ ↓ and Vim j k both work everywhere",
            completed=False,
            priority=Priority.LOW,
        ),
        Task(
            project_id="inbox",
            title="Press [n] or [a] to add a task, [e] or [Enter] to edit",
            completed=False,
            priority=Priority.NONE,
        ),
        Task(
            project_id="inbox",
            title="Press [1], [2], [3] to set priority, [t] for due date",
            completed=False,
            priority=Priority.NONE,
        ),
        Task(
            project_id="inbox",
            title="Press [d] or [Delete] to remove any task",
            completed=False,
            priority=Priority.NONE,
        ),
        Task(
            project_id="inbox",
            title="Press [/] anytime to search & filter tasks",
            completed=False,
            priority=Priority.NONE,
        ),
        Task(
            project_id="work",
            title="Review weekly team milestones",
            completed=False,
            priority=Priority.HIGH,
            due_date=today.isoformat(),
        ),
        Task(
            project_id="personal",
            title="Pick up groceries (milk, fruits, coffee)",
            completed=True,
            priority=Priority.LOW,
        ),
    ]

    return projects, tasks


class Storage:
    def __init__(self, data_path: Path = DEFAULT_DATA_FILE):
        self.data_path = data_path
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Tuple[List[Project], List[Task]]:
        if not self.data_path.exists():
            projects, tasks = get_default_seed()
            self.save(projects, tasks)
            return projects, tasks

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            projects = [Project.from_dict(p) for p in data.get("projects", [])]
            tasks = [Task.from_dict(t) for t in data.get("tasks", [])]

            if not projects:
                projects = [Project(id="inbox", name="Inbox", icon="📥")]

            return projects, tasks
        except Exception:
            projects, tasks = get_default_seed()
            return projects, tasks

    def save(self, projects: List[Project], tasks: List[Task]) -> None:
        data = {
            "version": 1,
            "projects": [p.to_dict() for p in projects],
            "tasks": [t.to_dict() for t in tasks],
        }

        # Atomic write
        temp_dir = self.data_path.parent
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name

        os.replace(temp_name, self.data_path)
