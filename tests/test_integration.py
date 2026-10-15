import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from toru.ui.app import ToruApp


async def test_toru():
    app = ToruApp()
    async with app.run_test() as pilot:
        print("[1] Toru app mounted successfully!")

        # Verify initial widgets
        assert pilot.app.query_one("#projects-list") is not None
        assert pilot.app.query_one("#tasks-list") is not None
        print("[2] Projects and Tasks lists found.")

        # Test space to toggle task
        target_task = pilot.app.get_highlighted_task()
        initial_completed = target_task.completed
        await pilot.press("space")
        updated_task = next(t for t in pilot.app.tasks if t.id == target_task.id)
        assert updated_task.completed != initial_completed
        print(f"[3] Space toggled task completion: {initial_completed} -> {updated_task.completed}")

        # Toggle back
        target_task.completed = initial_completed
        pilot.app.refresh_tasks_list()

        # Test priority setting with '1' (High)
        await pilot.press("1")
        assert pilot.app.get_highlighted_task().priority.name == "HIGH"
        print("[4] Priority 1 (High) set successfully.")

        # Test priority setting with '2' (Medium)
        await pilot.press("2")
        assert pilot.app.get_highlighted_task().priority.name == "MEDIUM"
        print("[5] Priority 2 (Medium) set successfully.")

        # Test down arrow navigation
        first_idx = pilot.app.query_one("#tasks-list").highlighted
        await pilot.press("down")
        second_idx = pilot.app.query_one("#tasks-list").highlighted
        assert second_idx == first_idx + 1
        print(f"[6] Down arrow navigated successfully: {first_idx} -> {second_idx}")

        # Test 'k' vim up navigation
        await pilot.press("k")
        back_idx = pilot.app.query_one("#tasks-list").highlighted
        assert back_idx == first_idx
        print(f"[7] Vim 'k' navigated back up: {second_idx} -> {back_idx}")

        # Test Tab to switch pane
        await pilot.press("tab")
        assert pilot.app.query_one("#projects-list").has_focus
        print("[8] Tab successfully switched focus to Projects pane.")

        # Test left arrow / right arrow pane navigation
        await pilot.press("right")
        assert pilot.app.query_one("#tasks-list").has_focus
        print("[9] Right arrow successfully switched focus to Tasks pane.")

        await pilot.press("left")
        assert pilot.app.query_one("#projects-list").has_focus
        print("[10] Left arrow successfully switched focus to Projects pane.")

        await pilot.press("tab")  # back to tasks

        # Test Help modal
        await pilot.press("question_mark")
        await pilot.pause()
        assert len(pilot.app.screen_stack) > 1  # Modal is active
        print("[11] Help modal displayed.")
        await pilot.press("escape")
        await pilot.pause()
        assert len(pilot.app.screen_stack) == 1
        print("[12] Help modal dismissed.")

        # Test Search / Filter
        await pilot.press("slash")
        await pilot.pause()
        assert pilot.app.query_one("#filter-input").has_focus
        print("[13] Filter input opened on '/'")
        await pilot.press("escape")
        await pilot.pause()
        assert not pilot.app.query_one("#filter-input").has_focus
        print("[14] Filter closed on Escape.")

        print("\nAll 14 automated tests passed perfectly!")


if __name__ == "__main__":
    asyncio.run(test_toru())
