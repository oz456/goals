import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from work.ui.app import WorkApp


async def test_work():
    app = WorkApp()
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

        # Test Enter goes INTO the workspace
        await pilot.press("enter")
        assert pilot.app.query_one("#workspace-list").has_focus
        print("[5] Enter successfully opened workspace!")

        # Test Space toggles completion in workspace
        current_goal = pilot.app.get_current_goal()
        first_item_done = current_goal.items[0].done
        await pilot.press("space")
        assert current_goal.items[0].done != first_item_done
        print(f"[6] Space toggled short-term goal: {first_item_done} -> {current_goal.items[0].done}")

        # Toggle back
        await pilot.press("space")

        # Test Escape goes BACK to Major Goals pane
        await pilot.press("escape")
        assert pilot.app.query_one("#goals-list").has_focus
        print("[7] Escape stepped back out to Major Goals.")

        # Test inline new goal creation
        await pilot.press("n")
        assert pilot.app.query_one("#goals-input").has_focus
        print("[8] 'n' opened inline goal input.")
        await pilot.press("escape")
        assert pilot.app.query_one("#goals-list").has_focus
        print("[9] Escape canceled input cleanly.")

        # Test dd double tap to delete
        initial_goals_count = len(pilot.app.goals)
        await pilot.press("d")  # single tap
        await pilot.pause()
        assert len(pilot.app.goals) == initial_goals_count
        print("[10] Single 'd' tap safely did not delete.")
        await pilot.press("d")  # quick second tap -> dd
        await pilot.pause()
        assert len(pilot.app.goals) == initial_goals_count - 1
        print("[11] Quick 'dd' successfully deleted item!")

        print("\nAll 11 tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_work())
