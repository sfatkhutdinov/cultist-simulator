# Safety API

Safety Library - Critical safety validation for agent actions.

Public API:
- validate_action(action, context) -> ValidationResult
- is_within_bounds(point, bounds) -> bool
- is_key_blacklisted(key, modifiers) -> bool
- check_rate_limit(action_history, max_actions_per_second) -> bool
- log_violation(violation_type, details) -> None

CRITICAL: This library MUST have 100% reliability (NFR-004).
Safety violations could affect the system outside the game.

All validation functions must complete in <10ms (NFR performance requirement).

**Module**: `src.safety`  
**Generated**: 2025-10-04 22:36:32

---

## Table of Contents

- [Functions](#functions)
- [Classes](#classes)

---

## Functions


### `check_rate_limit(action_history: List[Any], max_actions_per_second: int = 10) -> bool`

Check if action rate is within allowed limits.

T066: Rate limiting validation.
CRITICAL: Must complete in <10ms.

Args:
    action_history: List of recent actions (with timestamps)
    max_actions_per_second: Maximum allowed action rate
    
Returns:
    True if rate is acceptable, False if rate limit exceeded

---

### `get_logger(name: str = None)`

Get a logger instance.

Args:
    name: Optional logger name (typically __name__)

Returns:
    Structlog logger instance

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

### `is_within_bounds(point: src.lib.types.Point, bounds: src.lib.types.Rect) -> bool`

Check if a point is within the specified bounds.

T064: Spatial containment validation.
CRITICAL: Must complete in <1ms.

Args:
    point: Point to check
    bounds: Rectangle defining valid area
    
Returns:
    True if point is inside bounds, False otherwise

---

### `log_violation(violation_type: str, details: Dict[str, Any], severity: str = 'WARNING') -> None`

Log a safety violation to file.

T078: Safety violation logging for audit trail.

Args:
    violation_type: Type of violation (e.g., "OUT_OF_BOUNDS", "BLACKLISTED_KEY")
    details: Additional details about the violation
    severity: Severity level ("WARNING", "ERROR", "CRITICAL")

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

## Classes


### `class Action`

Represents an action to be performed by the agent.
T041: Implement Action entity.

**Methods:**


#### `__init__(self, action_type: src.lib.types.ActionType, parameters: Dict[str, Any], timestamp: datetime.datetime = <factory>, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class ActionType`

Types of actions the agent can perform.

---

### `class ConstraintType`

Types of safety constraints.

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

### `class ValidationResult`

Result of a safety validation check.

**Methods:**


#### `__init__(self, is_allowed: bool, reason: Optional[str] = None, constraints_violated: List[src.lib.types.ConstraintType] = <factory>, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---
