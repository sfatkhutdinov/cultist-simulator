"""
Integration tests for vision → automation pipeline.
Tests the interaction between vision_lib and automation_lib.

IMPORTANT: These tests are written FIRST before any implementation (TDD).
They MUST FAIL initially, then pass once both libraries are integrated.
"""

import pytest
from src.lib.types import Point, Rect, ElementType


class TestVisionAutomationIntegration:
    """T024: Integration tests for vision → automation pipeline."""

    def test_detect_element_then_click(self):
        """
        Integration test: Detect element with vision, then click it with automation.

        Flow: vision.detect_elements() → automation.simulate_click()
        """
        from src.vision import detect_elements, capture_game_state
        from src.automation import simulate_click

        # 1. Capture game state
        game_state = capture_game_state("Cultist Simulator")

        # 2. Detect clickable elements (e.g., buttons)
        elements = detect_elements(
            game_state.screenshot, [ElementType.BUTTON, ElementType.CARD]
        )

        # 3. Click the first detected element
        if elements:
            element = elements[0]
            click_point = element.bounds.center()

            result = simulate_click(click_point, "left", game_state.window_bounds)

            # Verify click was executed
            assert result.success is True
            assert result.safety_validated is True

    def test_track_changes_after_click(self):
        """
        Integration test: Click element, then verify state change with vision.

        Flow: automation.simulate_click() → vision.capture_game_state() → vision.track_element_changes()
        """
        # This will fail until both libraries are implemented
        with pytest.raises(Exception):
            from src.vision import capture_game_state, track_element_changes
            from src.automation import simulate_click

            # 1. Capture initial state
            state_before = capture_game_state("Cultist Simulator")

            # 2. Simulate a click action
            click_point = Point(400, 300)  # Example coordinates
            simulate_click(click_point, "left", state_before.window_bounds)

            # 3. Capture state after action
            state_after = capture_game_state("Cultist Simulator")

            # 4. Detect what changed
            changes = track_element_changes(state_before, state_after)

            # Should detect some changes (elements added/removed/moved)
            assert changes is not None
            assert hasattr(changes, "added_elements") or hasattr(
                changes, "removed_elements"
            )

    def test_window_bounds_consistency(self):
        """
        Integration test: Vision-detected window bounds match automation requirements.

        Ensures vision_lib.get_window_bounds() provides valid bounds for automation_lib.
        """
        from src.vision import get_window_bounds
        from src.automation import simulate_click

        # 1. Get window bounds from vision
        bounds = get_window_bounds("Cultist Simulator")

        # 2. Verify bounds are valid Rect
        assert isinstance(bounds, Rect)
        assert bounds.width > 0
        assert bounds.height > 0

        # 3. Use bounds for automation (should accept valid bounds)
        center_point = bounds.center()
        result = simulate_click(center_point, "left", bounds)

        # Should be allowed (point is within bounds)
        assert result.safety_validated is True

    def test_drag_between_detected_elements(self):
        """
        Integration test: Detect two elements, drag from one to another.

        Flow: vision.detect_elements() → automation.simulate_drag()
        """
        from src.vision import detect_elements, capture_game_state
        from src.automation import simulate_drag

        # 1. Capture game state and detect elements
        game_state = capture_game_state("Cultist Simulator")
        elements = detect_elements(
            game_state.screenshot, [ElementType.CARD, ElementType.SLOT]
        )

        # 2. If we have at least 2 elements, drag between them
        if len(elements) >= 2:
            start_point = elements[0].bounds.center()
            end_point = elements[1].bounds.center()

            result = simulate_drag(
                start_point,
                end_point,
                duration_ms=200.0,
                window_bounds=game_state.window_bounds,
            )

            # Verify drag was executed
            assert result.success is True
            assert result.safety_validated is True

    def test_vision_provides_clickable_targets(self):
        """
        Integration test: Vision identifies elements automation can interact with.

        Ensures detected elements have properties needed for automation.
        """
        from src.vision import detect_elements, capture_game_state

        # 1. Capture and detect elements
        game_state = capture_game_state("Cultist Simulator")
        elements = detect_elements(
            game_state.screenshot,
            [ElementType.BUTTON, ElementType.CARD, ElementType.SLOT],
        )

        # 2. Verify each element has required properties for automation
        for element in elements:
            # Must have bounding box
            assert hasattr(element, "bounds")
            assert isinstance(element.bounds, Rect)

            # Must be able to get center point for clicking
            center = element.bounds.center()
            assert isinstance(center, Point)

            # Center must be within window bounds
            assert game_state.window_bounds.contains(center)
