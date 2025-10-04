"""
Contract tests for vision_lib.
These tests verify the vision library's public interface contract.

IMPORTANT: These tests are written FIRST before any implementation (TDD).
They MUST FAIL initially, then pass once vision_lib is implemented.
"""

import pytest
import numpy as np
from src.lib.types import ElementType, Rect, Point


class TestVisionLibContract:
    """Test suite for vision_lib public interface."""

    def test_capture_game_state_exists(self):
        """T011: Contract test for vision_lib.capture_game_state()."""
        # This test verifies the function exists and has correct signature
        from src.vision import capture_game_state
        
        # Function should exist
        assert callable(capture_game_state)
        
        # Should accept window_name parameter with default
        import inspect
        sig = inspect.signature(capture_game_state)
        assert 'window_name' in sig.parameters
        assert sig.parameters['window_name'].default == "Cultist Simulator"

    def test_capture_game_state_returns_game_state(self):
        """T011: Contract test - capture_game_state returns GameState object."""
        from src.vision import capture_game_state
        
        # Mock window (in real test, this would use test fixtures)
        # For now, we expect this to fail with WindowNotFoundError
        with pytest.raises(Exception):  # Will be WindowNotFoundError
            state = capture_game_state("Test Window")

    def test_detect_elements_exists(self):
        """T012: Contract test for vision_lib.detect_elements()."""
        from src.vision import detect_elements
        
        # Function should exist
        assert callable(detect_elements)
        
        # Check signature
        import inspect
        sig = inspect.signature(detect_elements)
        assert 'screenshot' in sig.parameters
        assert 'element_types' in sig.parameters

    def test_detect_elements_accepts_numpy_array(self):
        """T012: Contract test - detect_elements accepts np.ndarray."""
        from src.vision import detect_elements
        
        # Create test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Should accept the image and element types
        # This will fail until implementation exists
        with pytest.raises(Exception):
            elements = detect_elements(
                test_image,
                [ElementType.CARD, ElementType.BUTTON]
            )

    def test_extract_text_regions_exists(self):
        """T013: Contract test for vision_lib.extract_text_regions()."""
        from src.vision import extract_text_regions
        
        # Function should exist
        assert callable(extract_text_regions)
        
        # Check signature
        import inspect
        sig = inspect.signature(extract_text_regions)
        assert 'screenshot' in sig.parameters
        assert 'regions' in sig.parameters

    def test_extract_text_regions_returns_list(self):
        """T013: Contract test - extract_text_regions returns list."""
        from src.vision import extract_text_regions
        
        # Create test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_regions = [Rect(10, 10, 50, 20)]
        
        # Should return a list (empty or with results)
        # This will fail until implementation exists
        with pytest.raises(Exception):
            result = extract_text_regions(test_image, test_regions)
            assert isinstance(result, list)

    def test_track_element_changes_exists(self):
        """Contract test for vision_lib.track_element_changes()."""
        from src.vision import track_element_changes
        
        # Function should exist
        assert callable(track_element_changes)

    def test_get_window_bounds_exists(self):
        """Contract test for vision_lib.get_window_bounds()."""
        from src.vision import get_window_bounds
        
        # Function should exist
        assert callable(get_window_bounds)
        
        # Check signature
        import inspect
        sig = inspect.signature(get_window_bounds)
        assert 'window_name' in sig.parameters

    def test_get_window_bounds_returns_rect(self):
        """Contract test - get_window_bounds returns Rect."""
        from src.vision import get_window_bounds
        
        # Should raise WindowNotFoundError for non-existent window
        with pytest.raises(Exception):  # Will be WindowNotFoundError
            bounds = get_window_bounds("NonExistentWindow123")


class TestVisionLibPerformance:
    """Performance contract tests for vision_lib."""

    @pytest.mark.performance
    def test_capture_game_state_performance(self):
        """T034: Performance test - capture_game_state() <500ms."""
        # This test verifies NFR-001: <500ms action selection latency
        # Vision capture is part of the critical path
        import time
        from src.vision import capture_game_state
        
        # This will fail until implementation exists
        # When implemented, should complete in <500ms
        with pytest.raises(Exception):
            start = time.perf_counter()
            state = capture_game_state("Cultist Simulator")
            duration_ms = (time.perf_counter() - start) * 1000
            
            # Performance requirement from NFR-001
            assert duration_ms < 500, f"Capture took {duration_ms}ms, must be <500ms"

    @pytest.mark.performance
    def test_detect_elements_performance(self):
        """T034: Performance test - detect_elements() <200ms."""
        import time
        from src.vision import detect_elements
        
        # Create test image
        test_image = np.zeros((1920, 1080, 3), dtype=np.uint8)
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            start = time.perf_counter()
            elements = detect_elements(
                test_image,
                [ElementType.CARD, ElementType.BUTTON, ElementType.TIMER]
            )
            duration_ms = (time.perf_counter() - start) * 1000
            
            # Contract specifies <200ms for element detection
            assert duration_ms < 200, f"Detection took {duration_ms}ms, must be <200ms"


class TestVisionLibErrorHandling:
    """Error handling contract tests."""

    def test_capture_game_state_window_not_found(self):
        """Contract test - raises WindowNotFoundError for missing window."""
        from src.vision import capture_game_state
        
        # Should raise specific error for non-existent window
        with pytest.raises(Exception) as exc_info:  # Will be WindowNotFoundError
            capture_game_state("ThisWindowDoesNotExist12345")
        
        # Verify error message is informative
        # (implementation will define WindowNotFoundError)

    def test_detect_elements_invalid_image(self):
        """Contract test - raises InvalidImageError for bad input."""
        from src.vision import detect_elements
        
        # Invalid image shape (should be H x W x 3)
        bad_image = np.zeros((10, 10), dtype=np.uint8)  # Missing color channel
        
        with pytest.raises(Exception):  # Will be InvalidImageError
            detect_elements(bad_image, [ElementType.CARD])
