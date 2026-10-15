from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import uuid


@dataclass
class GoalItem:
    """A short-term, specific goal / action step."""
    text: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    done: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoalItem":
        return cls(
            id=data.get("id", uuid.uuid4().hex[:8]),
            text=data.get("text", ""),
            done=data.get("done", False),
        )


@dataclass
class Goal:
    """A major goal with its own focused workspace."""
    title: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    items: List[GoalItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Goal":
        raw_items = data.get("items", [])
        items = [GoalItem.from_dict(it) for it in raw_items]
        return cls(
            id=data.get("id", uuid.uuid4().hex[:8]),
            title=data.get("title", "Untitled Goal"),
            items=items,
        )


@dataclass
class Workspace:
    """A window / workspace containing major goals and their tasks."""
    title: str = "Main"
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    goals: List[Goal] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "goals": [g.to_dict() for g in self.goals],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workspace":
        raw_goals = data.get("goals", [])
        goals = [Goal.from_dict(g) for g in raw_goals]
        return cls(
            id=data.get("id", uuid.uuid4().hex[:8]),
            title=data.get("title", "Main"),
            goals=goals,
        )

