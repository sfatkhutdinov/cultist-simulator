"""
Input Simulator - Low-level macOS input event generation

This module uses Quartz (CoreGraphics) to generate mouse and keyboard events
on macOS. All functions operate at the OS level and should only be called
after safety validation.

WARNING: These functions directly control the mouse and keyboard.
They MUST only be called after validation by the automation layer.

Functions:
- click_at_point(x, y, button): Generate mouse click event
- drag_between_points(x1, y1, x2, y2, duration_ms): Generate drag event
- press_key_combination(key, modifiers): Generate keyboard event
"""

from typing import List, Optional
import time

try:
    import Quartz
    from Quartz import (
        CGEventCreateMouseEvent,
        CGEventPost,
        CGEventCreateKeyboardEvent,
        CGEventSetFlags,
        kCGEventLeftMouseDown,
        kCGEventLeftMouseUp,
        kCGEventRightMouseDown,
        kCGEventRightMouseUp,
        kCGEventOtherMouseDown,
        kCGEventOtherMouseUp,
        kCGEventMouseMoved,
        kCGEventKeyDown,
        kCGEventKeyUp,
        kCGHIDEventTap,
        kCGEventFlagMaskCommand,
        kCGEventFlagMaskShift,
        kCGEventFlagMaskAlternate,
        kCGEventFlagMaskControl,
    )

    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False
    # Provide mock implementations for testing on non-macOS
    pass

from src.lib.logging_config import get_logger

logger = get_logger(__name__)


# Key code mappings for common keys
KEY_CODES = {
    "a": 0x00,
    "b": 0x0B,
    "c": 0x08,
    "d": 0x02,
    "e": 0x0E,
    "f": 0x03,
    "g": 0x05,
    "h": 0x04,
    "i": 0x22,
    "j": 0x26,
    "k": 0x28,
    "l": 0x25,
    "m": 0x2E,
    "n": 0x2D,
    "o": 0x1F,
    "p": 0x23,
    "q": 0x0C,
    "r": 0x0F,
    "s": 0x01,
    "t": 0x11,
    "u": 0x20,
    "v": 0x09,
    "w": 0x0D,
    "x": 0x07,
    "y": 0x10,
    "z": 0x06,
    "0": 0x1D,
    "1": 0x12,
    "2": 0x13,
    "3": 0x14,
    "4": 0x15,
    "5": 0x17,
    "6": 0x16,
    "7": 0x1A,
    "8": 0x1C,
    "9": 0x19,
    "return": 0x24,
    "enter": 0x24,
    "escape": 0x35,
    "delete": 0x33,
    "tab": 0x30,
    "space": 0x31,
    "`": 0x32,
    "f1": 0x7A,
    "f2": 0x78,
    "f3": 0x63,
    "f4": 0x76,
    "f5": 0x60,
    "f6": 0x61,
    "f7": 0x62,
    "f8": 0x64,
    "f9": 0x65,
    "f10": 0x6D,
    "f11": 0x67,
    "f12": 0x6F,
    "left": 0x7B,
    "right": 0x7C,
    "down": 0x7D,
    "up": 0x7E,
}

# Modifier flag mappings
MODIFIER_FLAGS = {
    "cmd": kCGEventFlagMaskCommand,
    "command": kCGEventFlagMaskCommand,
    "shift": kCGEventFlagMaskShift,
    "alt": kCGEventFlagMaskAlternate,
    "option": kCGEventFlagMaskAlternate,
    "ctrl": kCGEventFlagMaskControl,
    "control": kCGEventFlagMaskControl,
}


def click_at_point(x: float, y: float, button: str = "left") -> None:
    """
    Generate a mouse click event at the specified coordinates.

    T061: Quartz-based mouse click simulation.

    WARNING: This function directly controls the mouse. It should only be
    called after safety validation has passed.

    Args:
        x: X coordinate (screen coordinates)
        y: Y coordinate (screen coordinates)
        button: Mouse button ("left", "right", "middle")

    Raises:
        RuntimeError: If Quartz is not available
        ValueError: If button type is invalid
    """
    if not QUARTZ_AVAILABLE:
        logger.warning("quartz_unavailable", action="click")
        raise RuntimeError("Quartz framework not available (macOS only)")

    # Select event types based on button
    if button == "left":
        down_event = kCGEventLeftMouseDown
        up_event = kCGEventLeftMouseUp
        button_number = 0
    elif button == "right":
        down_event = kCGEventRightMouseDown
        up_event = kCGEventRightMouseUp
        button_number = 1
    elif button == "middle":
        down_event = kCGEventOtherMouseDown
        up_event = kCGEventOtherMouseUp
        button_number = 2
    else:
        raise ValueError(f"Invalid button type: {button}")

    try:
        # Create mouse down event
        mouse_down = CGEventCreateMouseEvent(
            None, down_event, (x, y), button_number  # No event source
        )

        # Create mouse up event
        mouse_up = CGEventCreateMouseEvent(None, up_event, (x, y), button_number)

        # Post the events
        CGEventPost(kCGHIDEventTap, mouse_down)
        time.sleep(0.01)  # 10ms delay between down and up
        CGEventPost(kCGHIDEventTap, mouse_up)

        logger.debug("click_event_posted", x=x, y=y, button=button)

    except Exception as e:
        logger.error("click_event_failed", x=x, y=y, button=button, error=str(e))
        raise


def drag_between_points(
    x1: float, y1: float, x2: float, y2: float, duration_ms: float
) -> None:
    """
    Generate a mouse drag event from start to end point.

    T062: Quartz-based mouse drag simulation.

    Implements smooth dragging by interpolating intermediate points.

    WARNING: This function directly controls the mouse. It should only be
    called after safety validation has passed.

    Args:
        x1: Start X coordinate
        y1: Start Y coordinate
        x2: End X coordinate
        y2: End Y coordinate
        duration_ms: Duration of drag in milliseconds

    Raises:
        RuntimeError: If Quartz is not available
    """
    if not QUARTZ_AVAILABLE:
        logger.warning("quartz_unavailable", action="drag")
        raise RuntimeError("Quartz framework not available (macOS only)")

    try:
        # Mouse down at start position
        mouse_down = CGEventCreateMouseEvent(
            None, kCGEventLeftMouseDown, (x1, y1), 0  # Left button
        )
        CGEventPost(kCGHIDEventTap, mouse_down)

        # Calculate number of intermediate steps (at least 10 steps)
        num_steps = max(10, int(duration_ms / 10))  # One step per 10ms
        step_duration = duration_ms / num_steps / 1000.0  # Convert to seconds

        # Interpolate between start and end
        for i in range(1, num_steps + 1):
            t = i / num_steps  # Interpolation factor (0 to 1)
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            # Create mouse moved event (with button down)
            mouse_drag = CGEventCreateMouseEvent(
                None, kCGEventLeftMouseDragged, (x, y), 0
            )
            CGEventPost(kCGHIDEventTap, mouse_drag)

            time.sleep(step_duration)

        # Mouse up at end position
        mouse_up = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, (x2, y2), 0)
        CGEventPost(kCGHIDEventTap, mouse_up)

        logger.debug(
            "drag_event_posted",
            start=f"({x1}, {y1})",
            end=f"({x2}, {y2})",
            duration_ms=duration_ms,
            num_steps=num_steps,
        )

    except Exception as e:
        logger.error(
            "drag_event_failed",
            start=f"({x1}, {y1})",
            end=f"({x2}, {y2})",
            error=str(e),
        )
        raise


def press_key_combination(key: str, modifiers: Optional[List[str]] = None) -> None:
    """
    Generate a keyboard event for a key with optional modifiers.

    T063: Quartz-based keyboard input simulation.

    WARNING: This function directly controls the keyboard. It should only be
    called after safety validation has passed (especially blacklist checking).

    Args:
        key: The key to press (lowercase string or key name)
        modifiers: List of modifier keys (["cmd"], ["cmd", "shift"], etc.)

    Raises:
        RuntimeError: If Quartz is not available
        ValueError: If key is not recognized
    """
    if not QUARTZ_AVAILABLE:
        logger.warning("quartz_unavailable", action="keypress")
        raise RuntimeError("Quartz framework not available (macOS only)")

    if modifiers is None:
        modifiers = []

    # Get key code
    key_lower = key.lower()
    if key_lower not in KEY_CODES:
        raise ValueError(f"Unknown key: {key}")

    key_code = KEY_CODES[key_lower]

    # Calculate modifier flags
    modifier_flags = 0
    for mod in modifiers:
        mod_lower = mod.lower()
        if mod_lower in MODIFIER_FLAGS:
            modifier_flags |= MODIFIER_FLAGS[mod_lower]
        else:
            logger.warning("unknown_modifier", modifier=mod)

    try:
        # Create key down event
        key_down = CGEventCreateKeyboardEvent(None, key_code, True)
        if modifier_flags:
            CGEventSetFlags(key_down, modifier_flags)

        # Create key up event
        key_up = CGEventCreateKeyboardEvent(None, key_code, False)
        if modifier_flags:
            CGEventSetFlags(key_up, modifier_flags)

        # Post the events
        CGEventPost(kCGHIDEventTap, key_down)
        time.sleep(0.01)  # 10ms delay between down and up
        CGEventPost(kCGHIDEventTap, key_up)

        logger.debug(
            "keypress_event_posted", key=key, modifiers=modifiers, key_code=key_code
        )

    except Exception as e:
        logger.error(
            "keypress_event_failed", key=key, modifiers=modifiers, error=str(e)
        )
        raise


# Add missing event type for dragging
if QUARTZ_AVAILABLE:
    try:
        from Quartz import kCGEventLeftMouseDragged
    except ImportError:
        # Fallback value if not available in this version
        kCGEventLeftMouseDragged = 6
