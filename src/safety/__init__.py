"""
Safety Library - Critical safety validation for agent actions.

Public API:
- validate_action(action, context) -> ValidationResult
- is_within_bounds(point, bounds) -> bool
- is_key_blacklisted(key, modifiers) -> bool
- check_rate_limit(action_history, max_actions_per_second) -> bool

CRITICAL: This library MUST have 100% reliability (NFR-004).
Safety violations could affect the system outside the game.

All validation functions must complete in <10ms (NFR performance requirement).
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.lib.types import (
    Point, Rect, Action, ActionType, ValidationResult, 
    ConstraintType, BLACKLISTED_KEYS
)
from src.lib.logging_config import get_logger

logger = get_logger(__name__)

__all__ = [
    'validate_action',
    'is_within_bounds',
    'is_key_blacklisted',
    'check_rate_limit',
]


def is_within_bounds(point: Point, bounds: Rect) -> bool:
    """
    Check if a point is within the specified bounds.
    
    T064: Spatial containment validation.
    CRITICAL: Must complete in <1ms.
    
    Args:
        point: Point to check
        bounds: Rectangle defining valid area
        
    Returns:
        True if point is inside bounds, False otherwise
    """
    result = bounds.contains(point)
    
    logger.debug(
        "bounds_check",
        point=str(point),
        bounds=str(bounds),
        is_within=result
    )
    
    return result


def is_key_blacklisted(key: str, modifiers: Optional[List[str]] = None) -> bool:
    """
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
    """
    if modifiers is None:
        modifiers = []
    
    # Normalize key and modifiers to lowercase
    key = key.lower()
    modifiers = [m.lower() for m in modifiers]
    
    # Build key combination string
    if modifiers:
        # Sort modifiers for consistent comparison
        sorted_mods = sorted(modifiers)
        combo = "+".join(sorted_mods) + "+" + key
    else:
        combo = key
    
    # Check against blacklist
    is_blacklisted = combo in BLACKLISTED_KEYS
    
    logger.debug(
        "key_blacklist_check",
        key=key,
        modifiers=modifiers,
        combo=combo,
        is_blacklisted=is_blacklisted
    )
    
    return is_blacklisted


def check_rate_limit(
    action_history: List[Any],
    max_actions_per_second: int = 10
) -> bool:
    """
    Check if action rate is within allowed limits.
    
    T066: Rate limiting validation.
    CRITICAL: Must complete in <10ms.
    
    Args:
        action_history: List of recent actions (with timestamps)
        max_actions_per_second: Maximum allowed action rate
        
    Returns:
        True if rate is acceptable, False if rate limit exceeded
    """
    if not action_history:
        return True  # No history, allow action
    
    # Get current time
    current_time = time.time()
    
    # Count actions in the last second
    recent_actions = 0
    for action in action_history:
        # Handle both Action objects and dicts
        if isinstance(action, Action):
            action_time = action.timestamp.timestamp()
        elif isinstance(action, dict) and 'timestamp' in action:
            # Handle dict with timestamp (from tests)
            timestamp = action['timestamp']
            if isinstance(timestamp, datetime):
                action_time = timestamp.timestamp()
            else:
                action_time = float(timestamp)
        else:
            continue
        
        # Check if action was within last second
        if current_time - action_time <= 1.0:
            recent_actions += 1
    
    # Check if rate limit exceeded
    is_allowed = recent_actions < max_actions_per_second
    
    logger.debug(
        "rate_limit_check",
        recent_actions=recent_actions,
        max_allowed=max_actions_per_second,
        is_allowed=is_allowed
    )
    
    return is_allowed


def validate_action(action: Any, context: Dict[str, Any]) -> ValidationResult:
    """
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
    """
    start_time = time.perf_counter()
    
    constraints_violated = []
    blocked_reason = None
    
    # Handle both Action objects and dicts (for test compatibility)
    if isinstance(action, Action):
        action_type = action.action_type
        parameters = action.parameters
    elif isinstance(action, dict):
        action_type = action.get('action_type')
        parameters = action
    else:
        return ValidationResult(
            is_allowed=False,
            reason="Invalid action object",
            constraints_violated=[],
            metadata={}
        )
    
    # 1. CHECK WINDOW FOCUS (if required in context)
    if context.get('window_focused') is False:
        constraints_violated.append(ConstraintType.FOCUS_REQUIRED)
        blocked_reason = "Window must be focused before executing actions"
        
        logger.warning(
            "action_blocked_focus",
            action_type=str(action_type),
            reason=blocked_reason
        )
        
        return ValidationResult(
            is_allowed=False,
            reason=blocked_reason,
            constraints_violated=constraints_violated,
            metadata={'performance_ms': (time.perf_counter() - start_time) * 1000}
        )
    
    # 2. CHECK SPATIAL BOUNDS (for click/drag actions)
    if action_type == ActionType.CLICK or (isinstance(action, dict) and 'point' in parameters):
        window_bounds = context.get('window_bounds')
        
        if window_bounds is not None:
            # Get point from action
            point = parameters.get('point')
            
            # Validate point exists and is valid
            if point is None:
                constraints_violated.append(ConstraintType.WINDOW_BOUNDS)
                blocked_reason = "Click action requires valid point coordinates"
                
                logger.warning(
                    "action_blocked_bounds",
                    action_type=str(action_type),
                    point=None,
                    bounds=str(window_bounds),
                    reason=blocked_reason
                )
                
                return ValidationResult(
                    is_allowed=False,
                    reason=blocked_reason,
                    constraints_violated=constraints_violated,
                    metadata={'performance_ms': (time.perf_counter() - start_time) * 1000}
                )
            
            if not is_within_bounds(point, window_bounds):
                constraints_violated.append(ConstraintType.WINDOW_BOUNDS)
                blocked_reason = f"Click point {point} is outside window bounds {window_bounds}"
                
                logger.warning(
                    "action_blocked_bounds",
                    action_type=str(action_type),
                    point=str(point),
                    bounds=str(window_bounds),
                    reason=blocked_reason
                )
                
                return ValidationResult(
                    is_allowed=False,
                    reason=blocked_reason,
                    constraints_violated=constraints_violated,
                    metadata={'performance_ms': (time.perf_counter() - start_time) * 1000}
                )
    
    # 3. CHECK KEY BLACKLIST (for key press actions)
    if action_type == ActionType.KEY_PRESS or (isinstance(action, dict) and 'key' in parameters):
        key = parameters.get('key', '')
        modifiers = parameters.get('modifiers', [])
        
        if is_key_blacklisted(key, modifiers):
            constraints_violated.append(ConstraintType.KEY_BLACKLIST)
            blocked_reason = f"Key combination '{'+'.join(modifiers + [key])}' is blacklisted"
            
            logger.warning(
                "action_blocked_blacklist",
                action_type=str(action_type),
                key=key,
                modifiers=modifiers,
                reason=blocked_reason
            )
            
            return ValidationResult(
                is_allowed=False,
                reason=blocked_reason,
                constraints_violated=constraints_violated,
                metadata={'performance_ms': (time.perf_counter() - start_time) * 1000}
            )
    
    # 4. CHECK RATE LIMIT
    recent_actions = context.get('recent_actions', [])
    max_rate = context.get('max_actions_per_second', 10)
    
    if not check_rate_limit(recent_actions, max_rate):
        constraints_violated.append(ConstraintType.RATE_LIMIT)
        blocked_reason = f"Action rate exceeds {max_rate} actions/second"
        
        logger.warning(
            "action_blocked_rate_limit",
            action_type=str(action_type),
            max_rate=max_rate,
            recent_count=len(recent_actions),
            reason=blocked_reason
        )
        
        return ValidationResult(
            is_allowed=False,
            reason=blocked_reason,
            constraints_violated=constraints_violated,
            metadata={'performance_ms': (time.perf_counter() - start_time) * 1000}
        )
    
    # ALL CHECKS PASSED - Action is safe
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    logger.debug(
        "action_validated",
        action_type=str(action_type),
        is_allowed=True,
        performance_ms=elapsed_ms
    )
    
    return ValidationResult(
        is_allowed=True,
        reason="All safety checks passed",
        constraints_violated=[],
        metadata={'performance_ms': elapsed_ms}
    )


if __name__ == "__main__":
    # Test safety library
    print("Testing safety library...")
    
    try:
        # Test bounds checking
        bounds = Rect(100, 100, 800, 600)
        inside = Point(400, 400)
        outside = Point(50, 50)
        
        assert is_within_bounds(inside, bounds) is True
        assert is_within_bounds(outside, bounds) is False
        print("✓ Bounds checking works")
        
        # Test key blacklist
        assert is_key_blacklisted("q", ["cmd"]) is True
        assert is_key_blacklisted("w", ["cmd"]) is True
        assert is_key_blacklisted("a", []) is False
        print("✓ Key blacklist works")
        
        # Test rate limiting
        rapid_actions = [{"timestamp": time.time() - 0.01 * i} for i in range(20)]
        assert check_rate_limit(rapid_actions, max_actions_per_second=10) is False
        assert check_rate_limit([], max_actions_per_second=10) is True
        print("✓ Rate limiting works")
        
        # Test action validation
        valid_action = Action(
            action_type=ActionType.CLICK,
            parameters={"point": Point(400, 400)}
        )
        valid_context = {
            "window_bounds": bounds,
            "window_focused": True,
            "recent_actions": []
        }
        result = validate_action(valid_action, valid_context)
        assert result.is_allowed is True
        print("✓ Action validation works")
        
        # Test blocked action
        invalid_action = Action(
            action_type=ActionType.CLICK,
            parameters={"point": Point(50, 50)}  # Outside bounds
        )
        result = validate_action(invalid_action, valid_context)
        assert result.is_allowed is False
        assert ConstraintType.WINDOW_BOUNDS in result.constraints_violated
        print("✓ Action blocking works")
        
        print("\n✓ All safety library tests passed")
        
    except Exception as e:
        print(f"✗ Safety library test failed: {e}")
        import traceback
        traceback.print_exc()
