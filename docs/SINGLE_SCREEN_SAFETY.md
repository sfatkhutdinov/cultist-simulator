# Single-Screen Safety Features

## Overview

The autonomous agent is designed to work safely on **single-screen Mac setups** by strictly limiting all interactions to the active game window. This prevents accidental clicks or keypresses in other applications.

## Safety Mechanisms

### 1. Active Window Validation

**Before Starting:**
- Agent checks that Cultist Simulator window is **active and focused**
- If window is not active, agent refuses to start with clear error message
- Window bounds are captured and used for all subsequent actions

**During Episode:**
- Agent **continuously monitors** window focus status
- If window loses focus (user switches apps), agent **pauses immediately**
- Agent resumes only when game window regains focus

### 2. Strict Boundary Enforcement

**All mouse actions are validated:**
```python
# Every click/drag is checked against window bounds
if not is_within_bounds(point, window_bounds):
    raise OutOfBoundsError("Click outside game window blocked")
```

**Safety layers:**
1. Vision library captures exact window bounds
2. Safety library validates every coordinate
3. Automation library rejects out-of-bounds actions
4. All violations are logged to `data/logs/safety_violations.jsonl`

### 3. Emergency Stop

**Immediate shutdown via:**
- `F12` key press (when implemented)
- Programmatic call to `request_emergency_stop()`
- Window focus loss detection
- Critical error conditions

**When triggered:**
- All automation stops immediately
- Current state is saved
- Session is marked as interrupted
- Logs record the stop reason

### 4. Keyboard Blacklist

**Dangerous keys are blocked:**
- `Cmd+Q` (quit application)
- `Cmd+W` (close window)
- `Cmd+Tab` (switch application)
- `Cmd+\`` (switch window)
- Additional system-level shortcuts

**Effect:**
- Even if agent tries to press these keys, they are rejected
- Violations are logged
- Agent continues with next action

## Usage for Single-Screen Setup

### Starting the Agent

```bash
# 1. Open Cultist Simulator and make sure it's the ACTIVE window
# 2. Start the agent
python -m src.orchestrator.cli run --agent-id my_agent --window "Cultist Simulator"
```

**What happens:**
1. ✅ Agent verifies "Cultist Simulator" window is active
2. ✅ Agent captures exact window bounds (e.g., x=100, y=50, w=1600, h=900)
3. ✅ Agent begins episode with strict boundary enforcement
4. ❌ If window not active → **Agent refuses to start** with error message

### During Gameplay

**If you need to switch windows:**
1. Agent detects focus loss immediately
2. Agent pauses all actions
3. Do your work in other apps safely
4. Return focus to Cultist Simulator
5. Agent resumes automatically

**Emergency stop:**
- Press `F12` (planned feature)
- Or `Ctrl+C` in terminal running agent
- Agent saves state and stops cleanly

### Monitoring Safety

**Check violation logs:**
```bash
tail -f data/logs/safety_violations.jsonl
```

**Example violations logged:**
```json
{
  "timestamp": "2025-10-04T20:56:00",
  "violation_type": "OUT_OF_BOUNDS",
  "severity": "WARNING",
  "details": {
    "action_type": "CLICK",
    "point": "Point(x=2000, y=100)",
    "bounds": "Rect(x=100, y=50, w=1600, h=900)",
    "reason": "Click point outside window bounds"
  }
}
```

## Implementation Details

### Window Focus Detection

**File:** `src/automation/window_manager.py`

```python
def require_active_window(window_name: str) -> Rect:
    """
    SAFETY CRITICAL: Ensures window is active before ANY action.
    
    Returns: Window bounds
    Raises: RuntimeError if window not active
    """
    bounds = get_active_window_bounds(window_name)
    if bounds is None:
        raise RuntimeError(
            f"Window '{window_name}' is not active! "
            f"Please focus the game window before running the agent."
        )
    return bounds
```

### Continuous Monitoring

**File:** `src/orchestrator/agent_runner.py`

```python
# Main episode loop
while True:
    # Check window focus every step
    if not is_window_active(self.window_name):
        logger.warning("window_lost_focus - pausing")
        wait(1000)  # Wait for focus to return
        continue
    
    # Check emergency stop
    if is_emergency_stop_requested():
        logger.warning("emergency_stop_detected")
        break
    
    # Execute action (only if window active)
    execute_step()
```

### Boundary Validation

**File:** `src/safety/__init__.py`

```python
def validate_action(action, context):
    # Get window bounds from context
    window_bounds = context.get('window_bounds')
    point = action.get('point')
    
    # Validate point is inside window
    if not is_within_bounds(point, window_bounds):
        log_violation("OUT_OF_BOUNDS", {...})
        return ValidationResult(is_allowed=False)
    
    return ValidationResult(is_allowed=True)
```

## Testing

### Manual Test

1. Start Cultist Simulator
2. Run agent: `python -m src.orchestrator.cli run --agent-id test`
3. Switch to another app (e.g., Chrome)
4. Verify agent pauses (check logs)
5. Return to Cultist Simulator
6. Verify agent resumes

### Verification Checklist

- [ ] Agent refuses to start if game window not active
- [ ] Agent pauses when window loses focus
- [ ] Agent resumes when window regains focus
- [ ] All clicks are within game window bounds
- [ ] Out-of-bounds attempts are logged and blocked
- [ ] Emergency stop (Ctrl+C) works immediately
- [ ] No clicks occur in other applications

## Troubleshooting

**Problem:** Agent says "Window not active" but game is open

**Solution:** 
- Make sure game window is the **foreground window** (click on it)
- Check window name matches exactly: `"Cultist Simulator"`
- Check macOS permissions (Screen Recording, Accessibility)

**Problem:** Agent clicks outside game window

**Solution:**
- This should be impossible due to safety checks
- If it happens, **file a bug report immediately**
- Check `data/logs/safety_violations.jsonl` for violations

**Problem:** Agent doesn't resume after returning to game

**Solution:**
- Check logs for focus detection issues
- Verify game window name hasn't changed
- Try restarting agent

## Safety Guarantees

✅ **Guaranteed Safe:**
- All clicks are bounded by game window
- Focus loss immediately pauses agent
- Dangerous key combos are blacklisted
- All violations are logged

⚠️ **Best Practices:**
- Always start with game window focused
- Monitor logs during initial runs
- Test emergency stop before long training sessions
- Use `--max-actions` limit for initial testing

## Future Enhancements

- [ ] Visual indicator when agent is paused (focus lost)
- [ ] Implement actual F12 key listener (requires pynput)
- [ ] Multi-monitor support with explicit display selection
- [ ] Screenshot annotation showing clickable bounds
- [ ] Real-time boundary visualization overlay
