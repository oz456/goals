import json
import os
import tempfile
from pathlib import Path
from typing import List
from .models import Goal, GoalItem

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


class Storage:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[Goal]:
        if not self.path.exists():
            if OLD_WORK_FILE.exists():
                try:
                    with open(OLD_WORK_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    goals = [Goal.from_dict(g) for g in data]
                    if goals:
                        self.save(goals)
                        return goals
                except Exception:
                    pass
            goals = get_default_goals()
            self.save(goals)
            return goals

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            goals = [Goal.from_dict(g) for g in data]
            if not goals:
                goals = get_default_goals()
                self.save(goals)
            return goals
        except Exception:
            goals = get_default_goals()
            return goals

    def save(self, goals: List[Goal]) -> None:
        data = [g.to_dict() for g in goals]
        temp_dir = self.path.parent
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name
        os.replace(temp_name, self.path)
