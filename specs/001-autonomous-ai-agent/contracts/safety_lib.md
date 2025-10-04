# Safety Library Contract

**Library**: `safety_lib`  
**Purpose**: Enforce 100% reliable containment and constraint validation  
**Dependencies**: None (minimal dependencies for reliability)

---

## Public Interface

### Functions

#### `validate_action(action: Action, context: SafetyContext) -> ValidationResult`
Validates action against all safety constraints (FR-006 to FR-010, NFR-004).

**Input**: 
- Action to validate
- SafetyContext (window bounds, focus state, action history)

**Output**: ValidationResult (is_valid, violations, warnings)  
**Performance**: <10ms (critical path)  
**Errors**: None (returns validation result, never raises)

#### `is_within_bounds(point: Point, bounds: Rect) -> bool`
Checks if point is within allowed window bounds (FR-006).

**Input**: Point coordinates, window bounds  
**Output**: True if within bounds  
**Performance**: <1ms

#### `is_key_blacklisted(key: str, modifiers: List[str]) -> bool`
Checks if key combination is forbidden (FR-007, FR-008).

**Input**: Key and modifiers  
**Output**: True if blacklisted  
**Performance**: <1ms

#### `check_rate_limit(action_history: List[Action], max_per_second: float) -> bool`
Verifies action doesn't exceed rate limit.

**Input**: Recent actions, rate limit  
**Output**: True if within limit  
**Performance**: <5ms

### CLI Interface

```bash
safety_lib --validate-action action.json --context context.json [--output result.json]
safety_lib --check-bounds 500 300 --window-bounds "0,0,1920,1080"
safety_lib --check-key "q" --modifiers "command"
safety_lib --test-constraints [--adversarial]
```

---

## Data Contracts

### ValidationResult
```python
{
    "is_valid": bool,
    "constraint_violations": list[str],  # Empty if valid
    "warnings": list[str],  # Non-blocking issues
    "validation_time_ms": float,
    "corrected_action": Action | None  # If auto-correctable
}
```

### SafetyContext
```python
{
    "window_bounds": Rect,
    "window_has_focus": bool,
    "recent_actions": list[Action],
    "timestamp": datetime
}
```

---

## Safety Constraints (Enforced)

1. **Window Bounds** (FR-006): All clicks/drags MUST be within game window
2. **Key Blacklist** (FR-007, FR-008): Forbidden keys MUST be blocked
3. **Focus Required** (FR-009): Game window MUST have focus
4. **Rate Limiting**: Max 10 actions/second
5. **Exit Prevention** (FR-007): Block quit/close actions

**Critical**: Reliability requirement is 100% (NFR-004). No false negatives allowed.

---

## Testing Requirements

1. `test_validate_blocks_out_of_bounds()` - Bounds enforcement
2. `test_validate_blocks_quit_keys()` - Blacklist enforcement
3. `test_validate_blocks_unfocused_actions()` - Focus requirement
4. `test_validate_blocks_excessive_rate()` - Rate limiting
5. `test_validation_never_false_negative()` - 100% reliability (critical!)
6. `test_performance_under_10ms()` - Performance requirement

---

## Configuration

```python
safety_config = {
    "enforce_bounds": True,  # MUST be True
    "enforce_blacklist": True,  # MUST be True
    "enforce_focus": True,  # MUST be True
    "enforce_rate_limit": True,  # MUST be True
    "max_actions_per_second": 10,
    "blacklisted_keys": [
        "Cmd+Q", "Cmd+W", "Cmd+Tab", "Cmd+H", "Cmd+M", "Escape"
    ],
    "validation_logging": True  # Log all validations
}
```

**Note**: All enforce flags MUST be True in production. Cannot be disabled.
