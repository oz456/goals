import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from work.ui.app import WorkApp
from work.models import Goal, GoalItem
from work.storage import Storage


async def test_work():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_goals.json"
        storage = Storage(test_file)

        # Seed test data
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

        app = WorkApp()
        app.storage = storage

        async with app.run_test() as pilot:
            print("[1] Work (Toru) app mounted with Omarchy theme!")

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

            print("\nAll 15 integration tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_work())
