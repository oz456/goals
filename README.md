# Toru (取る)

An intuitive, modern, dual-pane project & task manager for the terminal. Built with [Textual](https://textual.textualize.io/).

---

## 🚀 Features

- **Intuitive Controls First**: Both arrow keys (<kbd>↑</kbd> <kbd>↓</kbd> <kbd>←</kbd> <kbd>→</kbd>) and Vim keys (<kbd>h</kbd> <kbd>j</kbd> <kbd>k</kbd> <kbd>l</kbd>) work everywhere out of the box.
- **Full Mouse Support**: Click to select projects or tasks, double-click to edit, scroll with wheel.
- **Dual-Pane Layout**:
  - **Left**: Smart Views (*All Tasks*, *Today & Overdue*, *High Priority*, *Completed*) + Custom Projects with real-time pending task counts.
  - **Right**: Tasks sorted intelligently (uncompleted first, high priority first, upcoming due dates first).
- **Subtasks & Checklists**: Press <kbd>s</kbd> on any task to add and check off subtasks with mini progress counters (`[1/3]`).
- **Human-Friendly Due Dates**: Supports natural language dates: `today`, `tomorrow`, `friday`, `2d`, `1w`, or `YYYY-MM-DD`.
- **Urgency / Priority System**: One-key instant priority setting (`1`=🔴High, `2`=🟡Med, `3`=🔵Low, `4`=⚪None).
- **Live Search & Filter**: Press <kbd>/</kbd> to filter across tasks instantly.
- **Always-Visible Hotkeys**: Never memorize obscure commands; footer hints guide you at all times.

---

## ⌨️ Quick Reference

| Key | Action |
| :--- | :--- |
| <kbd>Tab</kbd> or <kbd>←</kbd> / <kbd>→</kbd> | Switch between **Projects** and **Tasks** panes |
| <kbd>↑</kbd> / <kbd>↓</kbd> or <kbd>j</kbd> / <kbd>k</kbd> | Move cursor up / down |
| <kbd>Space</kbd> | Toggle task complete (<span style="color:green">✔</span> / <span style="color:gray">◻</span>) |
| <kbd>n</kbd> or <kbd>a</kbd> | Add new task (or new project if focused on left pane) |
| <kbd>e</kbd> or <kbd>Enter</kbd> | Edit highlighted task (or rename project) |
| <kbd>d</kbd> or <kbd>Delete</kbd> | Delete highlighted task (or project) |
| <kbd>1</kbd> / <kbd>2</kbd> / <kbd>3</kbd> / <kbd>4</kbd> | Set priority (1=High, 2=Med, 3=Low, 4=None) |
| <kbd>p</kbd> | Cycle priority |
| <kbd>t</kbd> | Quick due date dialog (`today`, `tomorrow`, `3d`, etc.) |
| <kbd>s</kbd> | Manage subtasks |
| <kbd>/</kbd> | Open live search & filter |
| <kbd>?</kbd> | Open help cheatsheet |
| <kbd>q</kbd> | Quit cleanly |

---

## 💾 Storage

All your data is saved automatically and atomically as clean JSON in:
```
~/.local/share/toru/data.json
```
