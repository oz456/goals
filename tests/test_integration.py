import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from goals.ui.app import GoalsApp
from goals.models import Goal, GoalItem
from goals.storage import Storage


async def test_goals():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_goals.json"
        storage = Storage(test_file)

        # Seed test data in old format to verify auto-migration
        initial_goals = [
            Goal(
                title="Goal 1",
                items=[
                    GoalItem(text="Task 1A", done=False),
                    GoalItem(text="Task 1B", done=True),
                ],
            ),
            Goal(
                title="Goal 2",
                items=[
                    GoalItem(text="Task 2A", done=False),
                ],
            ),
        ]
        storage.save(initial_goals)

        app = GoalsApp()
        app.storage = storage

        async with app.run_test() as pilot:
            print("[1] Goals app mounted with Omarchy theme!")

            # Verify panes
            assert pilot.app.query_one("#goals-list") is not None
            assert pilot.app.query_one("#workspace-list") is not None
            assert pilot.app.query_one("#goals-list").has_focus
            print("[2] Dual panes found, starting focus on Major Goals.")

            # Test down arrow moves through major goals
            assert pilot.app.active_goal_idx == 0
            await pilot.press("down")
            assert pilot.app.active_goal_idx == 1
            print("[3] Down arrow navigated to next major goal.")

            await pilot.press("up")
            assert pilot.app.active_goal_idx == 0
            print("[4] Up arrow navigated back to first goal.")

            # Test Shift+Down / Shift+Up to rearrange Major Goals in Left Pane
            g0_title = pilot.app.goals[0].title
            g1_title = pilot.app.goals[1].title
            await pilot.press("shift+down")
            await pilot.pause()
            assert pilot.app.goals[0].title == g1_title
            assert pilot.app.goals[1].title == g0_title
            print("[5] Shift+Down reordered Major Goals in Left Pane!")

            await pilot.press("shift+up")
            await pilot.pause()
            assert pilot.app.goals[0].title == g0_title
            print("[6] Shift+Up reordered Major Goals back in Left Pane!")

            # Test Enter goes INTO the workspace
            await pilot.press("enter")
            assert pilot.app.query_one("#workspace-list").has_focus
            print("[7] Enter successfully opened workspace!")

            # Test Shift+Down / Shift+Up to rearrange Tasks in Workspace Pane
            curr_goal = pilot.app.get_current_goal()
            t0 = curr_goal.items[0].text
            t1 = curr_goal.items[1].text
            await pilot.press("shift+down")
            await pilot.pause()
            assert curr_goal.items[0].text == t1
            assert curr_goal.items[1].text == t0
            print("[8] Shift+Down reordered Tasks in Workspace Pane!")

            await pilot.press("shift+up")
            await pilot.pause()
            assert curr_goal.items[0].text == t0
            print("[9] Shift+Up reordered Tasks back in Workspace Pane!")

            # Test Space toggles completion in workspace
            first_item_done = curr_goal.items[0].done
            await pilot.press("space")
            assert curr_goal.items[0].done != first_item_done
            print(f"[10] Space toggled short-term goal: {first_item_done} -> {curr_goal.items[0].done}")

            # Test Escape goes BACK to Major Goals pane
            await pilot.press("escape")
            assert pilot.app.query_one("#goals-list").has_focus
            print("[11] Escape stepped back out to Major Goals.")

            # Test inline new goal creation
            await pilot.press("n")
            assert pilot.app.query_one("#goals-input").has_focus
            print("[12] 'n' opened inline goal input.")
            await pilot.press("escape")
            assert pilot.app.query_one("#goals-list").has_focus
            print("[13] Escape canceled input cleanly.")

            # Test dd double tap to delete
            initial_goals_count = len(pilot.app.goals)
            await pilot.press("d")  # single tap
            await pilot.pause()
            assert len(pilot.app.goals) == initial_goals_count
            print("[14] Single 'd' tap safely did not delete.")
            await pilot.press("d")  # quick second tap -> dd
            await pilot.pause()
            assert len(pilot.app.goals) == initial_goals_count - 1
            print("[15] Quick 'dd' successfully deleted item!")

            # --- Multi-Window / Workspace Tabs (Herdr style) ---
            # [16] Verify initial workspace tab
            assert len(pilot.app.workspaces) == 1
            assert pilot.app.workspaces[0].title == "Main"
            assert pilot.app.active_ws_idx == 0
            print("[16] Default workspace tab 'Main' loaded correctly.")

            # [17] Test New Window creation via alt+t
            await pilot.press("alt+t")
            tab_inp = pilot.app.query_one("#tab-input")
            assert tab_inp.has_focus
            tab_inp.value = "Personal"
            await pilot.press("enter")
            await pilot.pause()
            assert len(pilot.app.workspaces) == 2
            assert pilot.app.active_ws_idx == 1
            assert pilot.app.current_workspace.title == "Personal"
            print("[17] Alt+t successfully created new window 'Personal'!")

            # [18] Add goal inside new workspace 'Personal'
            await pilot.press("n")
            g_inp = pilot.app.query_one("#goals-input")
            g_inp.value = "Morning Run"
            await pilot.press("enter")
            await pilot.pause()
            assert len(pilot.app.goals) == 1
            assert pilot.app.goals[0].title == "Morning Run"
            print("[18] Successfully added new goal to 'Personal' window.")

            # [19] Test Alt+1 switches to Window 1 ('Main')
            await pilot.press("alt+1")
            await pilot.pause()
            assert pilot.app.active_ws_idx == 0
            assert pilot.app.current_workspace.title == "Main"
            assert "Morning Run" not in [g.title for g in pilot.app.goals]
            print("[19] Alt+1 switched back to 'Main', isolation verified!")

            # [20] Test Alt+2 switches to Window 2 ('Personal')
            await pilot.press("alt+2")
            await pilot.pause()
            assert pilot.app.active_ws_idx == 1
            assert pilot.app.current_workspace.title == "Personal"
            assert pilot.app.goals[0].title == "Morning Run"
            print("[20] Alt+2 switched to 'Personal' window.")

            # [21] Test Alt+Shift+Left rearranges tabs
            await pilot.press("alt+shift+left")
            await pilot.pause()
            assert pilot.app.active_ws_idx == 0
            assert pilot.app.workspaces[0].title == "Personal"
            assert pilot.app.workspaces[1].title == "Main"
            print("[21] Alt+Shift+Left successfully rearranged tabs!")

            # [22] Test Alt+r renames active window
            await pilot.press("alt+r")
            tab_inp = pilot.app.query_one("#tab-input")
            assert tab_inp.has_focus
            tab_inp.value = "Fitness"
            await pilot.press("enter")
            await pilot.pause()
            assert pilot.app.workspaces[0].title == "Fitness"
            print("[22] Alt+r successfully renamed window to 'Fitness'!")

            # [23] Test Alt+w closes active window
            await pilot.press("alt+w")
            await pilot.pause()
            assert len(pilot.app.workspaces) == 1
            assert pilot.app.current_workspace.title == "Main"
            print("[23] Alt+w successfully closed window, keeping 'Main'!")

            # [24] Test Alt+w does not close last remaining window
            await pilot.press("alt+w")
            await pilot.pause()
            assert len(pilot.app.workspaces) == 1
            print("[24] Safe close prevented deleting last remaining window.")

            # Create second tab again to test additional shortcuts
            await pilot.press("alt+t")
            t_inp = pilot.app.query_one("#tab-input")
            t_inp.value = "Projects"
            await pilot.press("enter")
            await pilot.pause()
            assert len(pilot.app.workspaces) == 2
            assert pilot.app.active_ws_idx == 1

            # [25] Test '[' and ']' bracket keys to cycle tabs
            await pilot.press("left_square_bracket")
            await pilot.pause()
            assert pilot.app.active_ws_idx == 0
            await pilot.press("right_square_bracket")
            await pilot.pause()
            assert pilot.app.active_ws_idx == 1
            print("[25] '[' and ']' successfully cycled tabs!")

            # [26] Test Alt+Left and Alt+Right to switch tabs
            await pilot.press("alt+left")
            await pilot.pause()
            assert pilot.app.active_ws_idx == 0
            await pilot.press("alt+right")
            await pilot.pause()
            assert pilot.app.active_ws_idx == 1
            print("[26] Alt+Left and Alt+Right successfully switched tabs!")

            # [27] Test Alt+H and Alt+L to rearrange tabs
            await pilot.press("alt+H")
            await pilot.pause()
            assert pilot.app.active_ws_idx == 0
            assert pilot.app.workspaces[0].title == "Projects"
            print("[27] Alt+H successfully swapped active tab position!")

            # [28] Verify no plus button in tab bar
            from goals.ui.widgets import HelpScreen
            tabs_render = str(pilot.app.query_one("#tabs-header").render())
            assert "+" not in tabs_render
            print("[28] Verified tab bar has no bloat / no '+' button!")

            # [29] Test '?' opens detailed Help modal
            await pilot.press("question_mark")
            await pilot.pause()
            assert isinstance(pilot.app.screen, HelpScreen)
            print("[29] '?' opened detailed HelpScreen modal!")

            # [30] Test '?' toggles Help modal closed
            await pilot.press("question_mark")
            await pilot.pause()
            assert not isinstance(pilot.app.screen, HelpScreen)
            print("[30] '?' closed HelpScreen modal!")

            # [31] Test 'Esc' closes Help modal
            await pilot.press("question_mark")
            await pilot.pause()
            assert isinstance(pilot.app.screen, HelpScreen)
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(pilot.app.screen, HelpScreen)
            print("[31] 'Esc' closed HelpScreen modal!")

            print("\nAll 31 integration tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_goals())


