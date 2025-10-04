# Automation Library Contract

**Library**: `automation_lib`  
**Purpose**: Generate and execute safe, sandboxed mouse and keyboard inputs to control the Cultist Simulator game  
**Dependencies**: Quartz (PyObjC), safety_lib

---

## Public Interface

### Functions

#### `simulate_click(point: Point, button: str = "left", window_bounds: Rect) -> ExecutionResult`
Simulates a mouse click at the specified coordinates.

**Input**:
- `point`: Screen coordinates to click (x, y)
- `button`: Mouse button ("left" | "right" | "middle")
- `window_bounds`: Game window bounds for safety validation

**Output**:
- `ExecutionResult` with:
  - `success`: bool
  - `execution_time_ms`: float
  - `safety_validated`: bool
  - `blocked_reason`: str | None

**Errors**:
- `OutOfBoundsError`: Click outside window_bounds (safety violation)
- `ExecutionFailedError`: System-level click simulation failed

**Safety**: MUST validate point is within window_bounds before execution (FR-006)

**Performance**: <50ms execution time

---

#### `simulate_drag(start: Point, end: Point, duration_ms: float, window_bounds: Rect) -> ExecutionResult`
Simulates a drag operation from start to end point.

**Input**:
- `start`: Starting coordinates
- `end`: Ending coordinates
- `duration_ms`: Drag duration (smooth interpolation)
- `window_bounds`: Game window bounds for safety

**Output**:
- `ExecutionResult` with success status and timing

**Errors**:
- `OutOfBoundsError`: Start or end outside window_bounds
- `InvalidDurationError`: Duration <10ms or >5000ms

**Safety**: Both start and end MUST be within window_bounds

**Performance**: Actual duration approximately `duration_ms` ± 20ms

---

#### `simulate_key_press(key: str, modifiers: List[str] = [], window_bounds: Rect) -> ExecutionResult`
Simulates a keyboard key press.

**Input**:
- `key`: Key to press (e.g., "a", "return", "space")
- `modifiers`: Modifier keys (e.g., ["shift"], ["command", "shift"])
- `window_bounds`: Game window bounds (for focus verification)

**Output**:
- `ExecutionResult` with success status

**Errors**:
- `BlacklistedKeyError`: Key combination forbidden (FR-007, FR-008)
- `WindowNotFocusedError`: Game window not focused (safety check)

**Safety**: 
- MUST check key against blacklist before execution
- MUST verify game window has focus
- Forbidden combinations: Cmd+Q, Cmd+W, Cmd+Tab, etc.

**Performance**: <20ms execution time

---

#### `wait(duration_ms: float) -> ExecutionResult`
Pauses execution for specified duration.

**Input**:
- `duration_ms`: Wait duration in milliseconds

**Output**:
- `ExecutionResult` with actual wait time

**Errors**: None (always succeeds)

**Performance**: Actual duration = `duration_ms` ± 5ms

---

#### `verify_window_focus(window_name: str) -> bool`
Checks if the game window currently has input focus.

**Input**:
- `window_name`: Name of window to check

**Output**:
- `True` if window focused, `False` otherwise

**Errors**: None (returns False on error)

**Performance**: <5ms

---

#### `get_blacklisted_keys() -> List[str]`
Returns list of forbidden key combinations.

**Output**:
- List of blacklisted key combinations (e.g., ["Cmd+Q", "Cmd+W", "Alt+F4"])

**Errors**: None

**Performance**: <1ms (returns cached list)

---

### CLI Interface

```bash
# Simulate click at coordinates
automation_lib --click x y [--button left|right|middle] --window-bounds "x,y,w,h"

# Simulate drag operation
automation_lib --drag start_x start_y end_x end_y --duration 500 --window-bounds "x,y,w,h"

# Simulate key press
automation_lib --key "a" [--modifiers "shift,command"] --window-bounds "x,y,w,h"

# Wait for duration
automation_lib --wait 1000

# Check window focus
automation_lib --verify-focus "Cultist Simulator"

# Get blacklisted keys
automation_lib --blacklist

# Test automation pipeline
automation_lib --test-safety [--window-bounds "x,y,w,h"]
```

**Output Format**: JSON to stdout with execution result. Errors to stderr.

---

## Data Contracts

### ExecutionResult
```python
{
    "success": bool,
    "execution_time_ms": float,
    "safety_validated": bool,
    "blocked_reason": str | None,
    "timestamp": "ISO-8601 datetime",
    "action_details": {
        "type": "click" | "drag" | "key_press" | "wait",
        "parameters": dict  # Action-specific params
    }
}
```

### Point
```python
{
    "x": int,
    "y": int
}
```

### Rect
```python
{
    "x": int,
    "y": int,
    "width": int,
    "height": int
}
```

---

## Error Handling

```python
class AutomationLibError(Exception):
    """Base error for automation library"""
    pass

class OutOfBoundsError(AutomationLibError):
    """Action coordinates outside allowed window bounds"""
    pass

class BlacklistedKeyError(AutomationLibError):
    """Key combination is forbidden by safety rules"""
    pass

class WindowNotFocusedError(AutomationLibError):
    """Game window does not have input focus"""
    pass

class ExecutionFailedError(AutomationLibError):
    """System-level input simulation failed"""
    pass

class InvalidDurationError(AutomationLibError):
    """Duration parameter out of valid range"""
    pass
```

---

## Configuration

```python
automation_config = {
    "window_name": "Cultist Simulator",
    "safety_validation_required": True,  # Enforce safety checks (always True in production)
    "blacklisted_keys": [
        "Cmd+Q",      # Quit application
        "Cmd+W",      # Close window
        "Cmd+Tab",    # Switch applications
        "Cmd+H",      # Hide application
        "Cmd+M",      # Minimize window
        "Cmd+`",      # Cycle windows
        "F11",        # Fullscreen toggle (might exit game view)
        "Escape"      # Sometimes exits menus/game
    ],
    "click_delay_ms": 10,       # Min delay between clicks
    "drag_smoothness": 0.01,    # Interpolation step size
    "focus_check_enabled": True,
    "max_actions_per_second": 10  # Rate limiting (FR-009)
}
```

---

## Safety Validation (Critical)

All action functions MUST perform these checks before execution:

1. **Bounds Check** (FR-006):
   ```python
   if not window_bounds.contains(point):
       raise OutOfBoundsError(f"Point {point} outside bounds {window_bounds}")
   ```

2. **Key Blacklist Check** (FR-007, FR-008):
   ```python
   key_combo = format_key_combo(key, modifiers)
   if key_combo in blacklisted_keys:
       raise BlacklistedKeyError(f"{key_combo} is forbidden")
   ```

3. **Focus Check** (FR-009):
   ```python
   if not verify_window_focus(window_name):
       raise WindowNotFocusedError("Game window not focused")
   ```

4. **Rate Limiting**:
   ```python
   time_since_last_action = now() - last_action_time
   if time_since_last_action < min_action_interval:
       wait(min_action_interval - time_since_last_action)
   ```

**Critical**: These checks MUST have 100% reliability (NFR-004). No action proceeds if any check fails.

---

## Testing Requirements

### Contract Tests
1. `test_click_within_bounds_succeeds()` - Valid click execution
2. `test_click_outside_bounds_raises_error()` - Safety validation
3. `test_blacklisted_key_raises_error()` - Key blacklist enforcement
4. `test_unfocused_window_raises_error()` - Focus requirement
5. `test_drag_interpolation_smoothness()` - Drag quality
6. `test_cli_outputs_valid_json()` - CLI contract

### Integration Tests
1. Execute click on real game window (with safety bounds)
2. Verify rate limiting prevents excessive actions
3. Test emergency stop mechanism
4. Adversarial test: attempt to bypass safety checks

### Safety Tests (Critical)
1. Attempt click outside bounds → MUST block
2. Attempt Cmd+Q → MUST block
3. Attempt action while window unfocused → MUST block
4. Flood actions beyond rate limit → MUST throttle
5. Test safety check performance (<10ms validation)

---

## Dependencies

```python
# requirements.txt for automation_lib
pyobjc-framework-Quartz>=9.0
pyobjc-framework-ApplicationServices>=9.0
numpy>=1.24.0  # For drag interpolation
```

---

## Initialization

```python
# Must be called before first use
automation_lib.initialize(config: dict) -> None

# Sets up Quartz CGEvent system, loads blacklist, initializes rate limiter
# Raises: InitializationError if system permissions insufficient
```

**macOS Permissions Required**:
- Accessibility permissions for input simulation
- Screen Recording permissions for focus verification

---

## Thread Safety

- `simulate_click()`: NOT thread-safe (sequential execution required)
- `simulate_drag()`: NOT thread-safe (sequential execution required)
- `simulate_key_press()`: NOT thread-safe (sequential execution required)
- `wait()`: Thread-safe
- `verify_window_focus()`: Thread-safe
- `get_blacklisted_keys()`: Thread-safe (immutable)

**Note**: All action functions MUST be called sequentially from a single thread to ensure safety validation order.

---

## Performance Benchmarks (Target)

| Operation | Target | Typical | Max Acceptable |
|-----------|--------|---------|----------------|
| simulate_click() | <50ms | 20ms | 80ms |
| simulate_drag() (500ms) | 500ms±20ms | 510ms | 550ms |
| simulate_key_press() | <20ms | 10ms | 30ms |
| wait() | exact | exact±5ms | exact±10ms |
| verify_window_focus() | <5ms | 2ms | 10ms |
| Safety validation | <10ms | 3ms | 15ms |

---

## Example Usage

```python
from automation_lib import simulate_click, simulate_drag, verify_window_focus
from vision_lib import get_window_bounds

# Initialize library
automation_lib.initialize(automation_config)

# Get game window bounds for safety
bounds = get_window_bounds("Cultist Simulator")

# Check focus before acting
if not verify_window_focus("Cultist Simulator"):
    raise Exception("Game not focused!")

# Simulate click on a button
try:
    result = simulate_click(Point(500, 300), button="left", window_bounds=bounds)
    if result.success:
        print(f"Click succeeded in {result.execution_time_ms}ms")
except OutOfBoundsError as e:
    print(f"Safety violation: {e}")

# Simulate drag operation
result = simulate_drag(
    start=Point(400, 200),
    end=Point(600, 400),
    duration_ms=300,
    window_bounds=bounds
)
```

```bash
# CLI usage
$ automation_lib --click 500 300 --window-bounds "0,0,1920,1080"
{
  "success": true,
  "execution_time_ms": 18.5,
  "safety_validated": true,
  "blocked_reason": null,
  ...
}

# Test safety - attempt dangerous action
$ automation_lib --key "q" --modifiers "command" --window-bounds "0,0,1920,1080"
ERROR: BlacklistedKeyError: Cmd+Q is forbidden
```

---

## Emergency Stop

Implement keyboard listener for emergency stop signal:

```python
# User presses F12 → immediately halt all automation
automation_lib.set_emergency_stop_key("F12")

# In action loop:
if automation_lib.emergency_stop_triggered():
    raise EmergencyStopError("User triggered emergency stop")
```

This provides manual override mechanism (FR-010).
