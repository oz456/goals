# Goals

A super minimal, distraction-free, 2-pane goal & workspace manager for the terminal, styled natively for **Omarchy**.

---

## 🎨 Philosophy

- **Zero Bloat**: No complicated priority tags, no overdue alarms, no nested clutter.
- **Pure 2-Pane Flow**:
  - **Left Pane**: Your **Major Goals** (e.g. *Launch Product*, *Health*, *Learning*).
  - **Right Pane**: The dedicated **Workspace** for the selected goal with immediate, short-term actionable steps.
- **Omarchy Native**: Automatically adapts to your active Omarchy theme colors (`colors.toml`) with live reloading.
- **Herdr-Style Multi-Window Tabs**: Organize goals into distinct workspaces (e.g. *Work*, *Personal*, *Research*) across the top bar.
- **Keyboard-First & Fluid**:
  - <kbd>↑</kbd> / <kbd>↓</kbd> (or <kbd>j</kbd>/<kbd>k</kbd>) to move.
  - <kbd>Shift</kbd> + <kbd>↑</kbd> / <kbd>↓</kbd> (or <kbd>K</kbd>/<kbd>J</kbd>) to rearrange items up or down.
  - <kbd>Enter</kbd> to step directly into the goal's workspace.
  - <kbd>Esc</kbd> to step back out to your major goals.
  - <kbd>Space</kbd> to check off a goal.
  - <kbd>n</kbd> to create a new goal or step inline.
  - <kbd>e</kbd> to edit.
  - <kbd>d</kbd><kbd>d</kbd> to remove.
  - <kbd>Alt</kbd> + <kbd>1..9</kbd> to jump directly to window tab.
  - <kbd>Alt</kbd> + <kbd>←</kbd> / <kbd>→</kbd> (or <kbd>[</kbd> / <kbd>]</kbd>) to switch window tabs.
  - <kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>←</kbd> / <kbd>→</kbd> (or <kbd>Alt</kbd>+<kbd>H</kbd>/<kbd>L</kbd>) to rearrange window tabs.
  - <kbd>Alt</kbd> + <kbd>t</kbd> (or click <kbd>[+]</kbd>) to create a new window.
  - <kbd>Alt</kbd> + <kbd>r</kbd> to rename the active window.
  - <kbd>Alt</kbd> + <kbd>w</kbd> to close the active window.
  - <kbd>q</kbd> to quit.

---

## ⌨️ Controls

| Key | Action | Context |
| :--- | :--- | :--- |
| <kbd>↑</kbd> / <kbd>↓</kbd> or <kbd>j</kbd> / <kbd>k</kbd> | Move selection up / down | Active pane |
| <kbd>Shift</kbd> + <kbd>↑</kbd> / <kbd>↓</kbd> or <kbd>K</kbd> / <kbd>J</kbd> | **Rearrange / move item up or down** | Active pane |
| <kbd>Enter</kbd> or <kbd>→</kbd> / <kbd>l</kbd> | **Open Workspace** (step into right pane) | Major Goals pane |
| <kbd>Esc</kbd> or <kbd>←</kbd> / <kbd>h</kbd> | **Back to Goals** (step back out to left pane) | Workspace pane |
| <kbd>Space</kbd> | Toggle completed (<span style="color:#2a9d8f">✔</span> / <span style="color:#5c5c5c">◻</span>) | Workspace pane |
| <kbd>n</kbd> or <kbd>a</kbd> | Add new item inline | Active pane |
| <kbd>e</kbd> | Edit highlighted item inline | Active pane |
| <kbd>d</kbd><kbd>d</kbd> or <kbd>Delete</kbd> | Delete highlighted item (double-tap <kbd>d</kbd>) | Active pane |
| <kbd>Tab</kbd> | Alternate between panes | Anywhere |
| <kbd>Alt</kbd> + <kbd>1..9</kbd> | Jump directly to window 1..9 | Top tab bar |
| <kbd>Alt</kbd> + <kbd>←</kbd> / <kbd>→</kbd> or <kbd>[</kbd> / <kbd>]</kbd> | Switch previous / next window tab | Anywhere |
| <kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>←</kbd> / <kbd>→</kbd> or <kbd>Alt</kbd>+<kbd>H</kbd>/<kbd>L</kbd> | **Rearrange active window tab left / right** | Anywhere |
| <kbd>Alt</kbd> + <kbd>t</kbd> / <kbd>Ctrl</kbd> + <kbd>t</kbd> or click <kbd>[+]</kbd> | **New window tab** | Anywhere |
| <kbd>Alt</kbd> + <kbd>r</kbd> / <kbd>Ctrl</kbd> + <kbd>r</kbd> | **Rename active window tab** | Anywhere |
| <kbd>Alt</kbd> + <kbd>w</kbd> / <kbd>Ctrl</kbd> + <kbd>w</kbd> | **Close active window tab** | Anywhere |
| <kbd>q</kbd> | Quit | Anywhere |

---

## 💾 Storage

Goals are saved automatically and atomically as clean JSON at:
```
~/.local/share/goals/goals.json
```
