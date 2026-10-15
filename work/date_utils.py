from datetime import datetime, date, timedelta
from typing import Optional, Tuple
import re
from dateutil import parser as date_parser

WEEKDAYS = {
    "mon": 0, "monday": 0,
    "tue": 1, "tues": 1, "tuesday": 1,
    "wed": 2, "wednesday": 2,
    "thu": 3, "thur": 3, "thurs": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}


def parse_due_date(text: str) -> Optional[date]:
    """Parse a flexible human-readable string into a date object."""
    if not text:
        return None

    cleaned = text.strip().lower()
    if not cleaned or cleaned in ("none", "clear", "no"):
        return None

    today = date.today()

    if cleaned in ("today", "tod"):
        return today

    if cleaned in ("tomorrow", "tmr", "tom"):
        return today + timedelta(days=1)

    if cleaned == "yesterday":
        return today - timedelta(days=1)

    # Relative days: "2d", "+3d", "5days"
    match_days = re.match(r"^\+?(\d+)\s*(?:d|day|days)?$", cleaned)
    if match_days:
        try:
            return today + timedelta(days=int(match_days.group(1)))
        except OverflowError:
            return None

    # Relative weeks: "1w", "+2w", "weeks"
    match_weeks = re.match(r"^\+?(\d+)\s*(?:w|wk|wks|week|weeks)$", cleaned)
    if match_weeks:
        try:
            return today + timedelta(weeks=int(match_weeks.group(1)))
        except OverflowError:
            return None

    # Weekdays like "friday", "next mon"
    is_next = cleaned.startswith("next ")
    weekday_str = cleaned.replace("next ", "").strip()
    if weekday_str in WEEKDAYS:
        target_weekday = WEEKDAYS[weekday_str]
        days_ahead = (target_weekday - today.weekday()) % 7
        if days_ahead == 0 or is_next:
            days_ahead += 7
        return today + timedelta(days=days_ahead)

    # General parser fallback (e.g. 2026-10-20, Oct 25, 10/25)
    try:
        dt = date_parser.parse(cleaned, default=datetime.now())
        return dt.date()
    except Exception:
        return None


def format_due_date_badge(due_str: Optional[str]) -> Tuple[str, str]:
    """
    Returns (badge_text, rich_style_or_color) for a given YYYY-MM-DD string.
    """
    if not due_str:
        return ("", "")

    try:
        due = date.fromisoformat(due_str)
    except ValueError:
        return (f"📅 {due_str}", "#cba6f7")

    today = date.today()
    diff = (due - today).days

    if diff < 0:
        overdue_days = abs(diff)
        day_text = f"{overdue_days}d ago" if overdue_days > 1 else "yesterday"
        return (f"⚠️ Overdue ({day_text})", "bold #f38ba8")
    elif diff == 0:
        return ("🔥 Today", "bold #fab387")
    elif diff == 1:
        return ("📅 Tomorrow", "bold #a6e3a1")
    elif 1 < diff <= 6:
        weekday = due.strftime("%A")
        return (f"📅 {weekday}", "#89dceb")
    else:
        return (f"📅 {due.strftime('%b %d')}", "#cba6f7")
