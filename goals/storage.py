import json
import os
import tempfile
from pathlib import Path
from typing import List, Any
from .models import Workspace, Goal, GoalItem

DATA_DIR = Path.home() / ".local" / "share" / "goals"
DATA_FILE = DATA_DIR / "goals.json"
OLD_WORK_FILE = Path.home() / ".local" / "share" / "work" / "goals.json"


def get_default_goals() -> List[Goal]:
    return [
        Goal(
            title="Launch Project",
            items=[
                GoalItem(text="Keep it super minimal and fast", done=True),
                GoalItem(text="Master arrow keys and Enter navigation", done=False),
                GoalItem(text="Track immediate short-term steps", done=False),
            ],
        ),
        Goal(
            title="Deep Work & Habits",
            items=[
                GoalItem(text="Morning focus block (90 mins)", done=False),
                GoalItem(text="Clear inbox & review goals", done=False),
            ],
        ),
    ]


def get_default_workspaces() -> List[Workspace]:
    return [
        Workspace(title="Main", goals=get_default_goals())
    ]


class Storage:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[Workspace]:
        if not self.path.exists():
            if OLD_WORK_FILE.exists():
                try:
                    with open(OLD_WORK_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list) and data:
                        if "goals" in data[0]:
                            workspaces = [Workspace.from_dict(w) for w in data]
                        else:
                            workspaces = [Workspace(title="Main", goals=[Goal.from_dict(g) for g in data])]
                        if workspaces:
                            self.save(workspaces)
                            return workspaces
                except Exception:
                    pass
            workspaces = get_default_workspaces()
            self.save(workspaces)
            return workspaces

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                if "goals" in data[0]:
                    workspaces = [Workspace.from_dict(w) for w in data]
                else:
                    workspaces = [Workspace(title="Main", goals=[Goal.from_dict(g) for g in data])]
                    # Migrate on disk to workspace format
                    self.save(workspaces)
            else:
                workspaces = get_default_workspaces()
                self.save(workspaces)
            return workspaces
        except Exception:
            workspaces = get_default_workspaces()
            return workspaces

    def save(self, items: List[Any]) -> None:
        if not items:
            data = []
        elif isinstance(items[0], Workspace):
            data = [w.to_dict() for w in items]
        elif isinstance(items[0], Goal):
            # Backward compatibility wrapper
            data = [Workspace(title="Main", goals=items).to_dict()]
        else:
            data = [x.to_dict() if hasattr(x, "to_dict") else x for x in items]

        temp_dir = self.path.parent
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name
        os.replace(temp_name, self.path)

