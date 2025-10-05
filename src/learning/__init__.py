"""
Learning Library - RL Agent and Knowledge Management

This library provides the "brain" of the autonomous agent:
- Action selection using reinforcement learning
- Experience replay and knowledge storage
- Loop detection to prevent stuck states
- Strategy evolution and articulation

Public API:
- select_action(game_state): Choose next action using RL policy
- update_knowledge(state, action, next_state, reward): Store experience
- detect_loop(action_history, window_size): Detect repeated patterns
- query_knowledge(query_type, parameters): Query knowledge base
- store_session(session): Persist session data

Performance Requirements (NFRs):
- NFR-001: select_action() <500ms
- NFR-003: query_knowledge() <100ms
- NFR-006: detect_loop() <10ms
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import time
import hashlib
from dataclasses import dataclass

from src.lib.types import GameState, Action, Session
from src.lib.logging_config import get_logger

# Export classes for CLI access
from .knowledge_base import KnowledgeBase
from .metrics import MetricsTracker
from .strategy import StrategyManager

logger = get_logger(__name__)


@dataclass
class QueryResult:
    """Result from knowledge base query."""

    result_count: int
    query_time_ms: float
    results: List[Any]
    metadata: Dict[str, Any]


# Placeholder for RL model (will be initialized lazily)
_rl_model = None
_knowledge_base = None

# Test mode flag - when True, uses random actions instead of requiring trained model
_test_mode = False


class ModelNotLoadedError(Exception):
    """Raised when RL model is not loaded/trained."""

    pass


class KnowledgeBaseError(Exception):
    """Raised when knowledge base operation fails."""

    pass


def enable_test_mode(enabled: bool = True) -> None:
    """
    Enable or disable test mode for action selection.

    When test mode is enabled, select_action() will use random valid actions
    instead of requiring a trained RL model. This is useful for testing and
    development.

    Args:
        enabled: Whether to enable test mode (default: True)
    """
    global _test_mode
    _test_mode = enabled
    if enabled:
        logger.info("test_mode_enabled", mode="random_actions")
    else:
        logger.info("test_mode_disabled", mode="requires_trained_model")


def select_action(game_state: Optional[GameState]) -> Action:
    """
    Select the next action to take based on current game state.

    T093: Action selection using trained RL policy.
    Performance requirement: <500ms (NFR-001)

    Uses Stable-Baselines3 PPO model to choose optimal action based on
    learned policy from previous episodes.

    Args:
        game_state: Current game state observation

    Returns:
        Action to execute

    Raises:
        ModelNotLoadedError: If RL model hasn't been trained yet
        ValueError: If game_state is None
    """
    start_time = time.perf_counter()

    if game_state is None:
        raise ValueError("game_state cannot be None")

    # Check if model is loaded (or test mode is enabled)
    global _rl_model, _test_mode
    if _rl_model is None and not _test_mode:
        logger.warning("rl_model_not_loaded")
        raise ModelNotLoadedError("RL model must be trained before action selection")

    try:
        # TODO T091-T092: Replace with actual PPO model inference
        # For now, return a placeholder/random action
        from src.lib.types import ActionType, Point
        import random

        # Generate random action for testing
        if _test_mode or _rl_model is None:
            # Random action within game window bounds
            window_bounds = game_state.window_bounds
            
            # Helper function to get random point in bounds
            def random_point():
                x = random.randint(
                    window_bounds.x + 50, window_bounds.x + window_bounds.width - 50
                )
                y = random.randint(
                    window_bounds.y + 50, window_bounds.y + window_bounds.height - 50
                )
                return Point(x, y)
            
            # Choose action type with weighted probabilities
            # 50% CLICK, 40% DRAG, 10% KEY_PRESS for diverse exploration
            action_type = random.choices(
                [ActionType.CLICK, ActionType.DRAG, ActionType.KEY_PRESS],
                weights=[0.5, 0.4, 0.1],
                k=1
            )[0]
            
            if action_type == ActionType.CLICK:
                # Click on element if available, otherwise random point
                if game_state.elements:
                    element = random.choice(game_state.elements)
                    point = element.center
                    rationale = f"Click on detected {element.element_type.value}"
                else:
                    point = random_point()
                    rationale = "Random click exploration"
                
                action = Action(
                    action_type=ActionType.CLICK,
                    parameters={"point": point},
                    metadata={
                        "confidence": 0.7 if game_state.elements else 0.5,
                        "rationale": rationale,
                        "test_mode": _test_mode,
                    },
                )
            
            elif action_type == ActionType.DRAG:
                # Drag between elements if available, otherwise random drag
                if len(game_state.elements) >= 2:
                    elem1, elem2 = random.sample(game_state.elements, 2)
                    start = elem1.center
                    end = elem2.center
                    rationale = f"Drag {elem1.element_type.value} to {elem2.element_type.value}"
                else:
                    start = random_point()
                    end = random_point()
                    rationale = "Random drag exploration"
                
                action = Action(
                    action_type=ActionType.DRAG,
                    parameters={
                        "start": start,
                        "end": end,
                        "duration": random.uniform(150, 400),  # 150-400ms drag
                    },
                    metadata={
                        "confidence": 0.7 if len(game_state.elements) >= 2 else 0.5,
                        "rationale": rationale,
                        "test_mode": _test_mode,
                    },
                )
            
            elif action_type == ActionType.KEY_PRESS:
                # Try common game keys (escape is blacklisted for safety)
                key = random.choice(["space", "tab", "return"])
                action = Action(
                    action_type=ActionType.KEY_PRESS,
                    parameters={"key": key},
                    metadata={
                        "confidence": 0.3,
                        "rationale": f"Try keyboard shortcut: {key}",
                        "test_mode": _test_mode,
                    },
                )
            
            else:
                # Fallback to click
                action = Action(
                    action_type=ActionType.CLICK,
                    parameters={"point": random_point()},
                    metadata={
                        "confidence": 0.5,
                        "rationale": "Fallback random click",
                        "test_mode": _test_mode,
                    },
                )
        else:
            # Real implementation with trained model:
            # observation = _encode_game_state(game_state)
            # action_vector, _states = _rl_model.predict(observation, deterministic=False)
            # action = _decode_action(action_vector)

            action = Action(
                action_type=ActionType.CLICK,
                parameters={"point": Point(400, 300)},
                metadata={
                    "confidence": 0.8,
                    "rationale": "Model-selected action",
                },
            )

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "action_selected",
            action_type=str(action.action_type),
            confidence=action.metadata.get("confidence", 0.0),
            duration_ms=duration_ms,
        )

        # Verify performance requirement
        if duration_ms >= 500:
            logger.warning(
                "action_selection_slow", duration_ms=duration_ms, threshold_ms=500
            )

        return action

    except Exception as e:
        logger.error("action_selection_failed", error=str(e))
        raise


def update_knowledge(
    state: Optional[Any],
    action: Optional[Any],
    next_state: Optional[Any],
    reward: float,
) -> None:
    """
    Update knowledge base with experience tuple (SARS).

    T094: Experience replay - store state, action, reward, next_state.
    Performance requirement: <100ms

    Stores experience in knowledge base for later training and analysis.

    Args:
        state: Current game state
        action: Action taken
        next_state: Resulting game state
        reward: Reward received

    Raises:
        KnowledgeBaseError: If storage fails
    """
    start_time = time.perf_counter()

    try:
        # TODO T095-T097: Implement actual knowledge base storage
        # For now, just log the experience

        global _knowledge_base
        if _knowledge_base is None:
            from .knowledge_base import KnowledgeBase

            _knowledge_base = KnowledgeBase()

        # Store experience (placeholder implementation)
        # In real implementation:
        # _knowledge_base.store_experience(state, action, next_state, reward)

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.debug("knowledge_updated", reward=reward, duration_ms=duration_ms)

        # Verify performance requirement
        if duration_ms >= 100:
            logger.warning(
                "knowledge_update_slow", duration_ms=duration_ms, threshold_ms=100
            )

    except Exception as e:
        logger.error("knowledge_update_failed", error=str(e))
        raise KnowledgeBaseError(f"Failed to update knowledge: {e}")


def detect_loop(action_history: List[Any], window_size: int = 30) -> bool:
    """
    Detect if agent is stuck in a repeated action loop.

    T099: Loop detection using sliding window and Levenshtein distance.
    Performance requirement: <10ms (NFR-006)

    Uses sliding window approach to identify repeated patterns in recent
    action history. Helps prevent the agent from getting stuck.

    Args:
        action_history: List of recent actions
        window_size: Size of sliding window (default: 30)

    Returns:
        True if loop detected, False otherwise
    """
    start_time = time.perf_counter()

    # Empty or very short history can't have loops
    if len(action_history) < 6:  # Need at least 2 repetitions of 3-action pattern
        return False

    try:
        # Simple loop detection: check if recent actions form a repeating pattern
        # TODO T076-T077: Implement proper Levenshtein distance comparison

        # Need minimum history for pattern detection
        if len(action_history) < 6:
            return False

        # Convert all to strings
        history_str = [str(a) for a in action_history]

        # Strategy: Check if the entire sequence is repetitive
        # by comparing different sliding windows

        # Try to detect patterns of size 2, 3, 4, 5
        for pattern_size in range(2, min(6, len(history_str) // 3 + 1)):
            # Check if last N items match a repeating pattern
            check_length = min(pattern_size * 3, len(history_str))
            if check_length < pattern_size * 2:
                continue

            recent_segment = history_str[-check_length:]

            # Check if this segment is repetitive
            # by seeing if it's made of the same pattern repeated
            pattern = recent_segment[:pattern_size]
            is_repetitive = True

            for i in range(pattern_size, len(recent_segment), pattern_size):
                segment = recent_segment[i : i + pattern_size]
                # Allow partial matches at the end
                match_length = min(len(segment), len(pattern))
                matches = sum(
                    1 for j in range(match_length) if segment[j] == pattern[j]
                )
                if matches / match_length < 0.8:  # 80% similarity threshold
                    is_repetitive = False
                    break

            if is_repetitive:
                duration_ms = (time.perf_counter() - start_time) * 1000

                logger.debug(
                    "loop_detection",
                    history_length=len(action_history),
                    window_size=window_size,
                    pattern_size=pattern_size,
                    pattern=pattern,
                    is_loop=True,
                    duration_ms=duration_ms,
                )

                return True

        # No repeating pattern found
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.debug(
            "loop_detection",
            history_length=len(action_history),
            window_size=window_size,
            is_loop=False,
            duration_ms=duration_ms,
        )

        # Verify performance requirement
        if duration_ms >= 10:
            logger.warning(
                "loop_detection_slow", duration_ms=duration_ms, threshold_ms=10
            )

        return False

    except Exception as e:
        logger.error("loop_detection_failed", error=str(e))
        # Return False on error (safer to not interrupt gameplay)
        return False


def query_knowledge(query_type: str, parameters: Dict[str, Any]) -> QueryResult:
    """
    Query the knowledge base for similar states, strategies, or mechanics.

    T097: Knowledge base queries with similarity search.
    Performance requirement: <100ms (NFR-003)

    Args:
        query_type: Type of query ("similar_states", "best_strategy", "mechanics")
        parameters: Query-specific parameters (e.g., state_hash, context)

    Returns:
        QueryResult with results and metadata

    Raises:
        KnowledgeBaseError: If query fails
    """
    start_time = time.perf_counter()

    try:
        # TODO T095-T097: Implement actual knowledge base queries
        # For now, return empty results

        global _knowledge_base
        if _knowledge_base is None:
            from .knowledge_base import KnowledgeBase

            _knowledge_base = KnowledgeBase()

        # Placeholder query (in real implementation, would query SQLite)
        results = []

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.debug(
            "knowledge_queried",
            query_type=query_type,
            result_count=len(results),
            duration_ms=duration_ms,
        )

        # Verify performance requirement
        if duration_ms >= 100:
            logger.warning(
                "knowledge_query_slow", duration_ms=duration_ms, threshold_ms=100
            )

        return QueryResult(
            result_count=len(results),
            query_time_ms=duration_ms,
            results=results,
            metadata={"query_type": query_type},
        )

    except Exception as e:
        logger.error("knowledge_query_failed", query_type=query_type, error=str(e))
        raise KnowledgeBaseError(f"Failed to query knowledge: {e}")


def store_session(session: Union[Session, Dict[str, Any], None]) -> str:
    """
    Store a complete session in the knowledge base.

    T096: Session persistence for later analysis and training.

    Args:
        session: Session object or dict to persist

    Returns:
        Session ID (UUID string or session_id from dict)

    Raises:
        KnowledgeBaseError: If storage fails
        ValueError: If session is None
    """
    if session is None:
        raise ValueError("session cannot be None")

    try:
        global _knowledge_base
        if _knowledge_base is None:
            from .knowledge_base import KnowledgeBase

            _knowledge_base = KnowledgeBase()

        # Handle dict input (from tests)
        if isinstance(session, dict):
            session_id = session.get("session_id", "")
            if not session_id:
                # Generate session ID from session data
                import json

                session_data = json.dumps(session, sort_keys=True).encode("utf-8")
                session_id = hashlib.sha256(session_data).hexdigest()[:16]

            logger.info("session_stored", session_id=session_id, source="dict")
            return session_id

        # Handle Session object
        # TODO T096: Implement actual session storage in database
        session_data = str(session).encode("utf-8")
        session_id = hashlib.sha256(session_data).hexdigest()[:16]

        logger.info("session_stored", session_id=session_id)

        return session_id

    except Exception as e:
        logger.error("session_storage_failed", error=str(e))
        raise KnowledgeBaseError(f"Failed to store session: {e}")


# Export public API
__all__ = [
    "select_action",
    "update_knowledge",
    "detect_loop",
    "query_knowledge",
    "store_session",
    "enable_test_mode",
    "QueryResult",
    "ModelNotLoadedError",
    "KnowledgeBaseError",
]
