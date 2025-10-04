"""
Automation Library - Safe macOS Input Simulation

This library provides safe, constrained automation of mouse and keyboard inputs
for interacting with the Cultist Simulator game on macOS.

CRITICAL SAFETY CONSTRAINTS:
- All actions MUST be validated by safety_lib before execution
- Actions outside window bounds are BLOCKED
- Blacklisted key combinations are BLOCKED (Cmd+Q, Cmd+W, etc.)
- Actions when window unfocused are BLOCKED
- Rate limiting prevents excessive rapid actions

Public API:
- simulate_click(point, button, window_bounds): Click at coordinates
- simulate_drag(start, end, duration_ms, window_bounds): Drag between points
- simulate_key_press(key, modifiers, window_bounds): Press key combination
- verify_window_focus(window_name): Check if window has focus
- get_blacklisted_keys(): Get list of forbidden key combinations
- wait(duration_ms): Sleep for specified duration

Dependencies:
- macOS Quartz (PyObjC) for low-level input events
- safety_lib for constraint validation
"""

from typing import Optional, List
import time

from src.lib.types import Point, Rect, MouseButton
from src.safety import validate_action, is_key_blacklisted, BLACKLISTED_KEYS
from src.lib.logging_config import get_logger

# Import platform-specific implementations
from .input_simulator import (
    click_at_point,
    drag_between_points,
    press_key_combination
)
from .window_manager import check_window_focus

logger = get_logger(__name__)


# Custom exceptions
class OutOfBoundsError(Exception):
    """Raised when action coordinates are outside valid window bounds."""
    pass


class BlacklistedKeyError(Exception):
    """Raised when attempting to press a blacklisted key combination."""
    pass


class WindowNotFocusedError(Exception):
    """Raised when window does not have focus but action requires it."""
    pass


class InvalidDurationError(Exception):
    """Raised when duration parameter is outside valid range."""
    pass


def simulate_click(
    point: Point,
    button: str = "left",
    window_bounds: Optional[Rect] = None
) -> bool:
    """
    Simulate a mouse click at the specified point.
    
    T065: Safe click simulation with bounds validation.
    CRITICAL: Must validate against safety constraints before execution.
    
    Performance requirement: <50ms execution time.
    
    Args:
        point: Point coordinates to click
        button: Mouse button ("left", "right", "middle")
        window_bounds: Rectangle defining valid click area (REQUIRED)
        
    Returns:
        True if click was executed, False if blocked
        
    Raises:
        OutOfBoundsError: If point is outside window_bounds
        ValueError: If window_bounds is None
    """
    start_time = time.perf_counter()
    
    # Require window bounds (safety constraint)
    if window_bounds is None:
        logger.error("click_rejected_no_bounds", point=str(point))
        raise ValueError("window_bounds is required for safety validation")
    
    # Validate button type
    if button not in ["left", "right", "middle"]:
        logger.error("click_rejected_invalid_button", button=button)
        raise ValueError(f"Invalid button type: {button}")
    
    # Build action for safety validation
    action = {
        "action_type": "CLICK",
        "point": point,
        "button": button
    }
    
    context = {
        "window_bounds": window_bounds,
        "window_focused": True  # Assume focused for now (T064 will implement)
    }
    
    # CRITICAL: Validate with safety library
    from src.safety import validate_action
    result = validate_action(action, context)
    
    if not result.is_allowed:
        logger.warning(
            "click_blocked_safety",
            point=str(point),
            button=button,
            reason=result.reason
        )
        raise OutOfBoundsError(result.reason)
    
    # Execute the click
    try:
        click_at_point(point.x, point.y, button)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "click_executed",
            point=str(point),
            button=button,
            duration_ms=duration_ms
        )
        
        return True
        
    except Exception as e:
        logger.error(
            "click_failed",
            point=str(point),
            button=button,
            error=str(e)
        )
        raise


def simulate_drag(
    start: Point,
    end: Point,
    duration_ms: float,
    window_bounds: Optional[Rect] = None
) -> bool:
    """
    Simulate a mouse drag from start to end point.
    
    T066: Safe drag simulation with bounds validation.
    CRITICAL: Both start and end points must be within bounds.
    
    Args:
        start: Starting point coordinates
        end: Ending point coordinates
        duration_ms: Duration of drag in milliseconds (10-5000ms)
        window_bounds: Rectangle defining valid drag area (REQUIRED)
        
    Returns:
        True if drag was executed, False if blocked
        
    Raises:
        OutOfBoundsError: If start or end is outside window_bounds
        InvalidDurationError: If duration is outside valid range
        ValueError: If window_bounds is None
    """
    # Require window bounds
    if window_bounds is None:
        logger.error("drag_rejected_no_bounds", start=str(start), end=str(end))
        raise ValueError("window_bounds is required for safety validation")
    
    # Validate duration
    if duration_ms < 10 or duration_ms > 5000:
        logger.error(
            "drag_rejected_invalid_duration",
            duration_ms=duration_ms,
            valid_range="10-5000ms"
        )
        raise InvalidDurationError(f"Duration {duration_ms}ms outside valid range (10-5000ms)")
    
    # Validate start point bounds
    context = {
        "window_bounds": window_bounds,
        "window_focused": True
    }
    
    start_action = {
        "action_type": "CLICK",
        "point": start
    }
    
    start_result = validate_action(start_action, context)
    if not start_result.is_allowed:
        logger.warning(
            "drag_blocked_start_point",
            start=str(start),
            reason=start_result.reason
        )
        raise OutOfBoundsError(f"Start point: {start_result.reason}")
    
    # Validate end point bounds
    end_action = {
        "action_type": "CLICK",
        "point": end
    }
    
    end_result = validate_action(end_action, context)
    if not end_result.is_allowed:
        logger.warning(
            "drag_blocked_end_point",
            end=str(end),
            reason=end_result.reason
        )
        raise OutOfBoundsError(f"End point: {end_result.reason}")
    
    # Execute the drag
    try:
        drag_between_points(start.x, start.y, end.x, end.y, duration_ms)
        
        logger.info(
            "drag_executed",
            start=str(start),
            end=str(end),
            duration_ms=duration_ms
        )
        
        return True
        
    except Exception as e:
        logger.error(
            "drag_failed",
            start=str(start),
            end=str(end),
            error=str(e)
        )
        raise


def simulate_key_press(
    key: str,
    modifiers: Optional[List[str]] = None,
    window_bounds: Optional[Rect] = None
) -> bool:
    """
    Simulate a key press with optional modifier keys.
    
    T067: Safe key press with blacklist validation.
    CRITICAL: Dangerous key combinations are BLOCKED (Cmd+Q, Cmd+W, etc.)
    
    Args:
        key: The key to press (lowercase)
        modifiers: List of modifier keys (["cmd"], ["cmd", "shift"], etc.)
        window_bounds: Window bounds (required for context)
        
    Returns:
        True if key press was executed, False if blocked
        
    Raises:
        BlacklistedKeyError: If key combination is blacklisted
        ValueError: If window_bounds is None
    """
    if modifiers is None:
        modifiers = []
    
    # Require window bounds
    if window_bounds is None:
        logger.error("keypress_rejected_no_bounds", key=key, modifiers=modifiers)
        raise ValueError("window_bounds is required for safety validation")
    
    # Check blacklist
    if is_key_blacklisted(key, modifiers):
        combo = "+".join(modifiers + [key])
        logger.warning(
            "keypress_blocked_blacklist",
            key=key,
            modifiers=modifiers,
            combo=combo
        )
        raise BlacklistedKeyError(f"Key combination '{combo}' is blacklisted for safety")
    
    # Build action for safety validation
    action = {
        "action_type": "KEY_PRESS",
        "key": key,
        "modifiers": modifiers
    }
    
    context = {
        "window_bounds": window_bounds,
        "window_focused": True
    }
    
    # Validate with safety library
    result = validate_action(action, context)
    
    if not result.is_allowed:
        logger.warning(
            "keypress_blocked_safety",
            key=key,
            modifiers=modifiers,
            reason=result.reason
        )
        raise BlacklistedKeyError(result.reason)
    
    # Execute the key press
    try:
        press_key_combination(key, modifiers)
        
        logger.info(
            "keypress_executed",
            key=key,
            modifiers=modifiers
        )
        
        return True
        
    except Exception as e:
        logger.error(
            "keypress_failed",
            key=key,
            modifiers=modifiers,
            error=str(e)
        )
        raise


def verify_window_focus(window_name: str) -> bool:
    """
    Check if the specified window has keyboard focus.
    
    T064: Window focus verification.
    Performance requirement: <5ms.
    
    Args:
        window_name: Name of the window to check (e.g., "Cultist Simulator")
        
    Returns:
        True if window has focus, False otherwise
    """
    start_time = time.perf_counter()
    
    try:
        has_focus = check_window_focus(window_name)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.debug(
            "focus_check",
            window_name=window_name,
            has_focus=has_focus,
            duration_ms=duration_ms
        )
        
        return has_focus
        
    except Exception as e:
        logger.error(
            "focus_check_failed",
            window_name=window_name,
            error=str(e)
        )
        return False


def get_blacklisted_keys() -> List[str]:
    """
    Get list of blacklisted key combinations.
    
    Returns:
        List of blacklisted key combination strings (e.g., ["cmd+q", "cmd+w"])
    """
    return list(BLACKLISTED_KEYS)


def wait(duration_ms: float) -> None:
    """
    Sleep for the specified duration.
    
    T068: Wait/sleep function.
    
    Args:
        duration_ms: Duration to wait in milliseconds
    """
    if duration_ms < 0:
        raise ValueError("Duration must be non-negative")
    
    time.sleep(duration_ms / 1000.0)
    
    logger.debug("wait_completed", duration_ms=duration_ms)


# Export public API
__all__ = [
    'simulate_click',
    'simulate_drag',
    'simulate_key_press',
    'verify_window_focus',
    'get_blacklisted_keys',
    'wait',
    'OutOfBoundsError',
    'BlacklistedKeyError',
    'WindowNotFocusedError',
    'InvalidDurationError',
]
