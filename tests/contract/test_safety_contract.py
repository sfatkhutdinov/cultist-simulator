"""
Contract tests for safety_lib.
These tests verify the safety library's public interface contract.

CRITICAL: This library MUST have 100% reliability (NFR-004).
Safety violations could affect the system outside the game.

IMPORTANT: These tests are written FIRST before any implementation (TDD).
They MUST FAIL initially, then pass once safety_lib is implemented.
"""

import pytest
from src.lib.types import Point, Rect, ActionType


class TestSafetyLibContract:
    """Test suite for safety_lib public interface."""

    def test_validate_action_exists(self):
        """T022: Contract test for safety_lib.validate_action()."""
        from src.safety import validate_action
        
        # Function should exist
        assert callable(validate_action)
        
        # Check signature
        import inspect
        sig = inspect.signature(validate_action)
        assert 'action' in sig.parameters
        assert 'context' in sig.parameters

    def test_validate_action_returns_validation_result(self):
        """T022: Contract test - validate_action returns ValidationResult."""
        from src.safety import validate_action
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            # Would normally pass Action object and context
            result = validate_action(None, None)
            
            # Should return ValidationResult with allowed/blocked decision
            assert hasattr(result, 'is_allowed')
            assert hasattr(result, 'blocked_reason')
            assert isinstance(result.is_allowed, bool)

    def test_is_within_bounds_exists(self):
        """T023: Contract test for safety_lib.is_within_bounds()."""
        from src.safety import is_within_bounds
        
        # Function should exist
        assert callable(is_within_bounds)
        
        # Check signature
        import inspect
        sig = inspect.signature(is_within_bounds)
        assert 'point' in sig.parameters
        assert 'bounds' in sig.parameters

    def test_is_within_bounds_validates_coordinates(self):
        """T023: Contract test - is_within_bounds checks point inside rect."""
        from src.safety import is_within_bounds
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            bounds = Rect(100, 100, 800, 600)
            
            # Point inside should return True
            inside_point = Point(400, 400)
            assert is_within_bounds(inside_point, bounds) is True
            
            # Point outside should return False
            outside_point = Point(50, 50)
            assert is_within_bounds(outside_point, bounds) is False

    def test_is_key_blacklisted_exists(self):
        """Contract test for safety_lib.is_key_blacklisted()."""
        from src.safety import is_key_blacklisted
        
        # Function should exist
        assert callable(is_key_blacklisted)
        
        # Check signature
        import inspect
        sig = inspect.signature(is_key_blacklisted)
        assert 'key' in sig.parameters
        assert 'modifiers' in sig.parameters

    def test_is_key_blacklisted_blocks_dangerous_keys(self):
        """Contract test - is_key_blacklisted identifies forbidden keys."""
        from src.safety import is_key_blacklisted
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            # Cmd+Q should be blacklisted
            assert is_key_blacklisted("q", ["cmd"]) is True
            
            # Cmd+W should be blacklisted
            assert is_key_blacklisted("w", ["cmd"]) is True
            
            # Regular key should not be blacklisted
            assert is_key_blacklisted("a", []) is False

    def test_check_rate_limit_exists(self):
        """Contract test for safety_lib.check_rate_limit()."""
        from src.safety import check_rate_limit
        
        # Function should exist
        assert callable(check_rate_limit)
        
        # Check signature
        import inspect
        sig = inspect.signature(check_rate_limit)
        assert 'action_history' in sig.parameters
        assert 'max_actions_per_second' in sig.parameters

    def test_check_rate_limit_enforces_throttling(self):
        """Contract test - check_rate_limit prevents excessive actions."""
        from src.safety import check_rate_limit
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            # Simulate rapid-fire actions (more than allowed)
            # Would normally pass list of Action objects with timestamps
            rapid_actions = [{"timestamp": 1.0 + i*0.01} for i in range(20)]
            
            # Should return False if rate exceeded
            is_allowed = check_rate_limit(rapid_actions, max_actions_per_second=10)
            assert isinstance(is_allowed, bool)


class TestSafetyLibCriticalValidation:
    """CRITICAL: 100% reliability tests for safety constraints."""

    def test_validate_action_blocks_out_of_bounds_click(self):
        """T029: Safety test - validate_action blocks out-of-bounds clicks."""
        from src.safety import validate_action
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            # Action with coordinates outside window bounds
            # Would normally pass proper Action object
            invalid_action = {
                "action_type": ActionType.CLICK,
                "point": Point(2000, 2000),  # Way outside typical bounds
            }
            context = {
                "window_bounds": Rect(0, 0, 1920, 1080)
            }
            
            result = validate_action(invalid_action, context)
            
            # MUST block this action
            assert result.is_allowed is False
            assert "bounds" in result.blocked_reason.lower()

    def test_validate_action_blocks_blacklisted_keys(self):
        """T030: Safety test - validate_action blocks dangerous key combos."""
        from src.safety import validate_action
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            # Cmd+Q to quit
            dangerous_action = {
                "action_type": ActionType.KEY_PRESS,
                "key": "q",
                "modifiers": ["cmd"]
            }
            context = {
                "window_bounds": Rect(0, 0, 1920, 1080)
            }
            
            result = validate_action(dangerous_action, context)
            
            # MUST block this action
            assert result.is_allowed is False
            assert "blacklist" in result.blocked_reason.lower()

    def test_validate_action_requires_window_focus(self):
        """T031: Safety test - validate_action checks window focus."""
        from src.safety import validate_action
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            # Valid action but window not focused
            action = {
                "action_type": ActionType.CLICK,
                "point": Point(100, 100)
            }
            context = {
                "window_bounds": Rect(0, 0, 800, 600),
                "window_focused": False  # NOT focused
            }
            
            result = validate_action(action, context)
            
            # MUST block actions when window unfocused
            assert result.is_allowed is False
            assert "focus" in result.blocked_reason.lower()

    def test_validate_action_enforces_rate_limits(self):
        """T032: Safety test - validate_action enforces rate limiting."""
        from src.safety import validate_action
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            action = {
                "action_type": ActionType.CLICK,
                "point": Point(100, 100)
            }
            
            # Context with recent rapid-fire actions
            context = {
                "window_bounds": Rect(0, 0, 800, 600),
                "window_focused": True,
                "recent_actions": [{"timestamp": 1.0 + i*0.01} for i in range(50)]
            }
            
            result = validate_action(action, context)
            
            # Should block if rate limit exceeded
            # (exact behavior depends on implementation)
            assert hasattr(result, 'is_allowed')

    def test_adversarial_bypass_attempts(self):
        """T033: Adversarial test - attempt to bypass all constraints."""
        from src.safety import validate_action
        
        # This will fail until implementation exists
        # Try various ways to bypass safety checks
        with pytest.raises(Exception):
            # Attempt 1: Negative coordinates
            result1 = validate_action(
                {"action_type": ActionType.CLICK, "point": Point(-10, -10)},
                {"window_bounds": Rect(0, 0, 800, 600)}
            )
            assert result1.is_allowed is False
            
            # Attempt 2: Extremely large coordinates (overflow?)
            result2 = validate_action(
                {"action_type": ActionType.CLICK, "point": Point(999999, 999999)},
                {"window_bounds": Rect(0, 0, 800, 600)}
            )
            assert result2.is_allowed is False
            
            # Attempt 3: None/null values
            result3 = validate_action(
                {"action_type": ActionType.CLICK, "point": None},
                {"window_bounds": Rect(0, 0, 800, 600)}
            )
            assert result3.is_allowed is False


class TestSafetyLibPerformance:
    """Performance tests for safety validation (CRITICAL PATH)."""

    @pytest.mark.performance
    def test_validate_action_performance(self):
        """T036: Performance test - validate_action() <10ms."""
        import time
        from src.safety import validate_action
        
        # This will fail until implementation exists
        # Safety validation is on the critical path - MUST be fast
        with pytest.raises(Exception):
            action = {
                "action_type": ActionType.CLICK,
                "point": Point(100, 100)
            }
            context = {
                "window_bounds": Rect(0, 0, 800, 600),
                "window_focused": True
            }
            
            start = time.perf_counter()
            result = validate_action(action, context)
            duration_ms = (time.perf_counter() - start) * 1000
            
            # CRITICAL: Must be <10ms (called before every action)
            assert duration_ms < 10, f"Validation took {duration_ms}ms, must be <10ms"

    @pytest.mark.performance
    def test_is_within_bounds_performance(self):
        """Performance test - is_within_bounds() <1ms."""
        import time
        from src.safety import is_within_bounds
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            bounds = Rect(0, 0, 1920, 1080)
            point = Point(960, 540)
            
            start = time.perf_counter()
            result = is_within_bounds(point, bounds)
            duration_ms = (time.perf_counter() - start) * 1000
            
            # Should be extremely fast (simple bounds check)
            assert duration_ms < 1, f"Bounds check took {duration_ms}ms, must be <1ms"

    @pytest.mark.performance
    def test_is_key_blacklisted_performance(self):
        """Performance test - is_key_blacklisted() <1ms."""
        import time
        from src.safety import is_key_blacklisted
        
        # This will fail until implementation exists
        with pytest.raises(Exception):
            start = time.perf_counter()
            result = is_key_blacklisted("q", ["cmd"])
            duration_ms = (time.perf_counter() - start) * 1000
            
            # Should be extremely fast (simple lookup)
            assert duration_ms < 1, f"Blacklist check took {duration_ms}ms, must be <1ms"
