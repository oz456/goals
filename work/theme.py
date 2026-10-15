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
    """Generate minimal, modern Textual CSS respecting Omarchy theme."""
    bg = theme["background"]
    dark_bg = theme["dark_background"]
    lighter_bg = theme["lighter_background"]
    fg = theme["foreground"]
    muted = theme["muted"]
    accent = theme["accent"]
    selection = theme["selection"]
    green = theme["green"]

    return f"""
    Screen {{
        background: {bg};
        color: {fg};
    }}

    #top-bar {{
        height: 2;
        dock: top;
        background: {dark_bg};
        padding: 0 2;
        color: {muted};
    }}

    #top-brand {{
        text-style: bold;
        color: {accent};
    }}

    #top-stats {{
        dock: right;
        color: {muted};
    }}

    #main-container {{
        height: 1fr;
        padding: 0 1;
    }}

    #goals-pane {{
        width: 38%;
        height: 100%;
        border: solid {lighter_bg};
        background: {bg};
        padding: 0 1;
        margin-right: 1;
    }}

    #goals-pane:focus-within {{
        border: solid {accent};
    }}

    #workspace-pane {{
        width: 62%;
        height: 100%;
        border: solid {lighter_bg};
        background: {bg};
        padding: 0 1;
    }}

    #workspace-pane:focus-within {{
        border: solid {accent};
    }}

    .pane-header {{
        height: 2;
        color: {muted};
        text-style: bold;
        padding: 0 1;
        border-bottom: solid {lighter_bg};
        margin-bottom: 1;
    }}

    .pane-header-active {{
        color: {accent};
    }}

    OptionList {{
        height: 1fr;
        background: transparent;
        border: none;
        padding: 0;
    }}

    OptionList:focus {{
        border: none;
    }}

    .inline-input {{
        height: 3;
        dock: bottom;
        background: {dark_bg};
        border: tall {accent};
        color: {fg};
        display: none;
        margin-bottom: 1;
    }}

    .inline-input.active {{
        display: block;
    }}

    #bottom-bar {{
        height: 1;
        dock: bottom;
        background: {dark_bg};
        color: {muted};
        padding: 0 2;
        text-align: center;
    }}
    """
