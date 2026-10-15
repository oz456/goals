from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from enum import IntEnum
from typing import List, Optional, Dict, Any
import uuid


class Priority(IntEnum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @property
    def label(self) -> str:
        return {
            Priority.NONE: "None",
            Priority.LOW: "Low",
            Priority.MEDIUM: "Medium",
            Priority.HIGH: "High",
        }[self]

    @property
    def badge(self) -> str:
        return {
            Priority.NONE: "",
            Priority.LOW: "🔵 Low",
            Priority.MEDIUM: "🟡 Med",
            Priority.HIGH: "🔴 High",
        }[self]

    @property
    def color(self) -> str:
        return {
            Priority.NONE: "dim",
            Priority.LOW: "#89b4fa",
            Priority.MEDIUM: "#f9e2af",
            Priority.HIGH: "#f38ba8",
        }[self]


@dataclass
class Subtask:
    title: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subtask":
        return cls(
            id=data.get("id", uuid.uuid4().hex[:8]),
            title=data.get("title", ""),
            completed=data.get("completed", False),
        )


@dataclass
class Task:
    title: str
    project_id: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    completed: bool = False
    priority: Priority = Priority.NONE
    due_date: Optional[str] = None  # Stored as YYYY-MM-DD
    notes: str = ""
    subtasks: List[Subtask] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "completed": self.completed,
            "priority": int(self.priority),
            "due_date": self.due_date,
            "notes": self.notes,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        subtasks_raw = data.get("subtasks", [])
        subtasks = [Subtask.from_dict(s) for s in subtasks_raw]
        priority_val = data.get("priority", 0)
        try:
            priority = Priority(priority_val)
        except ValueError:
            priority = Priority.NONE

        return cls(
            id=data.get("id", uuid.uuid4().hex[:8]),
            project_id=data.get("project_id", "inbox"),
            title=data.get("title", "Untitled Task"),
            completed=data.get("completed", False),
            priority=priority,
            due_date=data.get("due_date"),
            notes=data.get("notes", ""),
            subtasks=subtasks,
            created_at=data.get("created_at", datetime.now().isoformat()),
        )


@dataclass
class Project:
    name: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    icon: str = "📁"
    color: str = "#89b4fa"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        return cls(
            id=data.get("id", uuid.uuid4().hex[:8]),
            name=data.get("name", "New Project"),
            icon=data.get("icon", "📁"),
            color=data.get("color", "#89b4fa"),
        )
