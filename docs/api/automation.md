# Automation API

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

**Module**: `src.automation`  
**Generated**: 2025-10-04 22:36:32

---

## Table of Contents

- [Functions](#functions)
- [Classes](#classes)

---

## Functions


### `check_window_focus(window_name: str) -> bool`

Check if the specified window currently has keyboard focus.

T064: Window focus verification using Quartz.
Performance requirement: <10ms (iterates through window list).

Args:
    window_name: Name of the window to check (e.g., "Cultist Simulator")
    
Returns:
    True if window has focus, False otherwise

---

### `click_at_point(x: float, y: float, button: str = 'left') -> None`

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

---

### `drag_between_points(x1: float, y1: float, x2: float, y2: float, duration_ms: float) -> None`

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

---

### `get_blacklisted_keys() -> List[str]`

Get list of blacklisted key combinations.

Returns:
    List of blacklisted key combination strings (e.g., ["cmd+q", "cmd+w"])

---

### `get_logger(name: str = None)`

Get a logger instance.

Args:
    name: Optional logger name (typically __name__)

Returns:
    Structlog logger instance

---

### `is_emergency_stop_requested() -> bool`

Check if emergency stop has been requested.

T069: Emergency stop mechanism.

Returns:
    True if emergency stop was requested, False otherwise

---

### `is_key_blacklisted(key: str, modifiers: Optional[List[str]] = None) -> bool`

Check if a key combination is blacklisted.

T065: Key blacklist validation.
CRITICAL: Must complete in <1ms.

Blacklisted combinations:
- Cmd+Q (quit application)
- Cmd+W (close window)
- Cmd+Tab (switch application)
- Cmd+` (switch window)
- Escape (menu navigation that could exit)
- F4 (Alt+F4 equivalent)

Args:
    key: The key being pressed (lowercase)
    modifiers: List of modifier keys (cmd, alt, ctrl, shift)
    
Returns:
    True if key combination is blacklisted, False otherwise

---

### `press_key_combination(key: str, modifiers: Optional[List[str]] = None) -> None`

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

---

### `request_emergency_stop() -> None`

Request emergency stop of all automation.

T069: Emergency stop mechanism - call this to halt the agent.
Can be triggered by F12 key press or other emergency conditions.

---

### `reset_emergency_stop() -> None`

Reset emergency stop flag.

Call this to resume automation after emergency stop.

---

### `simulate_click(point: src.lib.types.Point, button: str = 'left', window_bounds: Optional[src.lib.types.Rect] = None) -> src.lib.types.ActionResult`

Simulate a mouse click at the specified point.

T065: Safe click simulation with bounds validation.
CRITICAL: Must validate against safety constraints before execution.

Performance requirement: <50ms execution time.

Args:
    point: Point coordinates to click
    button: Mouse button ("left", "right", "middle")
    window_bounds: Rectangle defining valid click area (REQUIRED)
    
Returns:
    ActionResult with success status and validation info
    
Raises:
    OutOfBoundsError: If point is outside window_bounds
    ValueError: If window_bounds is None

---

### `simulate_drag(start: src.lib.types.Point, end: src.lib.types.Point, duration_ms: float, window_bounds: Optional[src.lib.types.Rect] = None) -> src.lib.types.ActionResult`

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

---

### `simulate_key_press(key: str, modifiers: Optional[List[str]] = None, window_bounds: Optional[src.lib.types.Rect] = None) -> src.lib.types.ActionResult`

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

---

### `start_emergency_stop_listener() -> None`

Start background thread to listen for F12 key press.

T069: Emergency stop mechanism - F12 key listener.

Note: Implementing a global key listener on macOS requires
accessibility permissions and is complex. For now, this is
a placeholder. The emergency stop can be triggered programmatically
via request_emergency_stop().

TODO: Implement actual F12 key listener using pynput or similar.

---

### `validate_action(action: Any, context: Dict[str, Any]) -> src.lib.types.ValidationResult`

Validate an action against all safety constraints.

T067: Complete action validation.
CRITICAL: Must complete in <10ms and have 100% reliability.

This is the main safety validation function that combines all checks:
- Spatial containment (window bounds)
- Key blacklist
- Window focus requirement
- Rate limiting

Args:
    action: Action object or dict to validate
    context: Context dict with:
        - window_bounds: Rect defining valid click area
        - window_focused: bool indicating if window has focus
        - recent_actions: List of recent actions for rate limiting
        
Returns:
    ValidationResult with is_allowed flag and reason

---

### `verify_window_focus(window_name: str) -> bool`

Check if the specified window has keyboard focus.

T064: Window focus verification.
Performance requirement: <5ms.

Args:
    window_name: Name of the window to check (e.g., "Cultist Simulator")
    
Returns:
    True if window has focus, False otherwise

---

### `wait(duration_ms: float) -> None`

Sleep for the specified duration.

T068: Wait/sleep function.

Args:
    duration_ms: Duration to wait in milliseconds

---

## Classes


### `class ActionResult`

Result from executing an automation action.

**Methods:**


#### `__init__(self, success: bool, safety_validated: bool, blocked_reason: Optional[str] = None, duration_ms: Optional[float] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class BlacklistedKeyError`

Raised when attempting to press a blacklisted key combination.

---

### `class InvalidDurationError`

Raised when duration parameter is outside valid range.

---

### `class MouseButton`

Mouse button identifiers.

---

### `class OutOfBoundsError`

Raised when action coordinates are outside valid window bounds.

---

### `class Point`

A 2D point representing screen coordinates.

**Methods:**


#### `__init__(self, x: int, y: int) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class Rect`

A rectangle representing a bounding box.

**Methods:**


#### `__init__(self, x: int, y: int, width: int, height: int) -> None`

Initialize self.  See help(type(self)) for accurate signature.


#### `center(self) -> src.lib.types.Point`

Get the center point of the rectangle.


#### `contains(self, point: src.lib.types.Point) -> bool`

Check if a point is inside the rectangle.

---

### `class WindowNotFocusedError`

Raised when window does not have focus but action requires it.

---
