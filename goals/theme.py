import tomllib
from pathlib import Path
from typing import Dict, Any

THEME_FILE = Path.home() / ".local" / "state" / "omarchy" / "current" / "theme" / "colors.toml"

FALLBACK_THEME = {
    "background": "#0d0d0d",
    "dark_background": "#080808",
    "darker_background": "#030303",
    "lighter_background": "#1a1a1a",
    "selection": "#3a151b",
    "muted": "#5c5c5c",
    "accent": "#e63946",
    "foreground": "#f5f5f5",
    "dark_foreground": "#9e9e9e",
    "green": "#2a9d8f",
    "red": "#e63946",
    "yellow": "#f4a261",
    "cyan": "#457b9d",
}


def get_theme_mtime() -> float:
    """Return mtime of theme file to detect live changes."""
    try:
        return THEME_FILE.stat().st_mtime
    except Exception:
        return 0.0


def load_theme() -> Dict[str, str]:
    """Load colors from active Omarchy theme, or fallback to default."""
    if THEME_FILE.exists():
        try:
            with open(THEME_FILE, "rb") as f:
                data = tomllib.load(f)
                theme = dict(FALLBACK_THEME)
                theme.update(data)
                return theme
        except Exception:
            pass
    return dict(FALLBACK_THEME)


def generate_css(theme: Dict[str, str]) -> str:
    """Base layout structure for Textual."""
    return """
    Screen {
        background: #0d0d0d;
        color: #f5f5f5;
    }

    #top-bar {
        height: 1;
        dock: top;
        background: transparent;
        padding: 0 1;
    }

    #tabs-header {
        width: 100%;
        background: transparent;
    }

    #tab-input {
        dock: top;
        height: 3;
        margin: 0 1 1 1;
        background: #0d0d0d;
        border: tall #e63946;
        color: #f5f5f5;
        display: none;
    }

    #tab-input.active {
        display: block;
    }

    #main-container {
        height: 1fr;
        padding: 0 1;
    }

    #goals-pane {
        width: 38%;
        height: 100%;
        border: solid #1a1a1a;
        background: #0d0d0d;
        padding: 0 1;
        margin-right: 1;
    }

    #workspace-pane {
        width: 62%;
        height: 100%;
        border: solid #1a1a1a;
        background: #0d0d0d;
        padding: 0 1;
    }

    .pane-header {
        height: 2;
        color: #5c5c5c;
        text-style: bold;
        padding: 0 1;
        border-bottom: solid #1a1a1a;
        margin-bottom: 1;
    }

    OptionList {
        height: 1fr;
        background: transparent;
        border: none;
        padding: 0;
    }

    OptionList:focus {
        border: none;
    }

    .inline-input {
        height: 3;
        dock: bottom;
        background: #0d0d0d;
        border: tall #e63946;
        color: #f5f5f5;
        display: none;
        margin-bottom: 1;
    }

    .inline-input.active {
        display: block;
    }

    #bottom-bar {
        height: 1;
        dock: bottom;
        background: transparent;
        color: #5c5c5c;
        padding: 0 1;
        text-align: center;
        overflow: hidden;
    }
    """
