"""
Shared type definitions for Cultist Simulator AI Agent.
Provides common data structures used across all libraries.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ============================================================================
# Value Objects
# ============================================================================

@dataclass(frozen=True)
class Point:
    """A 2D point representing screen coordinates."""
    x: int
    y: int

    def __str__(self) -> str:
        return f"Point({self.x}, {self.y})"


@dataclass(frozen=True)
class Rect:
    """A rectangle representing a bounding box."""
    x: int
    y: int
    width: int
    height: int

    def center(self) -> Point:
        """Get the center point of the rectangle."""
        return Point(
            x=self.x + self.width // 2,
            y=self.y + self.height // 2
        )

    def contains(self, point: Point) -> bool:
        """Check if a point is inside the rectangle."""
        return (
            self.x <= point.x <= self.x + self.width and
            self.y <= point.y <= self.y + self.height
        )

    def __str__(self) -> str:
        return f"Rect(x={self.x}, y={self.y}, w={self.width}, h={self.height})"


# ============================================================================
# Enumerations
# ============================================================================

class ElementType(Enum):
    """Types of game elements that can be detected."""
    CARD = "card"
    BUTTON = "button"
    SLOT = "slot"
    TIMER = "timer"
    TEXT = "text"
    RESOURCE_INDICATOR = "resource_indicator"
    OTHER = "other"


class ActionType(Enum):
    """Types of actions the agent can perform."""
    CLICK = "click"
    DRAG = "drag"
    KEY_PRESS = "key_press"
    WAIT = "wait"
    COMPOSITE = "composite"  # Multiple actions in sequence


class CardState(Enum):
    """Possible states of a game card."""
    IN_HAND = "in_hand"
    IN_SLOT = "in_slot"
    DRAGGING = "dragging"
    DECAYING = "decaying"
    HIDDEN = "hidden"


class MetricType(Enum):
    """Types of performance metrics tracked."""
    WIN_RATE = "win_rate"
    SURVIVAL_TIME = "survival_time"
    RESOURCES_ACCUMULATED = "resources_accumulated"
    UNIQUE_ENDINGS = "unique_endings"
    LEARNING_RATE = "learning_rate"
    MECHANICS_DISCOVERED = "mechanics_discovered"


class ConstraintType(Enum):
    """Types of safety constraints."""
    WINDOW_BOUNDS = "window_bounds"
    KEY_BLACKLIST = "key_blacklist"
    FOCUS_REQUIRED = "focus_required"
    RATE_LIMIT = "rate_limit"


class ExecutionStatus(Enum):
    """Status of action execution."""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    PENDING = "pending"


class EndCondition(Enum):
    """How a game session ended."""
    GAME_OVER = "game_over"
    WIN = "win"
    CRASH = "crash"
    MANUAL_STOP = "manual_stop"
    TIMEOUT = "timeout"
    SAFETY_VIOLATION = "safety_violation"


# ============================================================================
# Button and Key Constants
# ============================================================================

class MouseButton(Enum):
    """Mouse button identifiers."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


# Blacklisted keys that could exit the game or affect the system
BLACKLISTED_KEYS = [
    "cmd+q",  # Quit application
    "cmd+w",  # Close window
    "cmd+tab",  # Switch application
    "cmd+`",  # Switch window
    "escape",  # Often used for menus that could exit
    "f4",  # Alt+F4 equivalent
]


# ============================================================================
# Configuration Constants
# ============================================================================

# Performance requirements from NFRs
MAX_ACTION_SELECTION_LATENCY_MS = 500
MAX_KNOWLEDGE_QUERY_LATENCY_MS = 100
MAX_SAFETY_VALIDATION_LATENCY_MS = 10

# Safety constraints
DEFAULT_RATE_LIMIT_ACTIONS_PER_SECOND = 10
LOOP_DETECTION_WINDOW_SIZE = 20
LOOP_DETECTION_SIMILARITY_THRESHOLD = 0.8

# Vision parameters
DEFAULT_SCREENSHOT_INTERVAL_MS = 500
DEFAULT_YOLO_CONFIDENCE_THRESHOLD = 0.5
DEFAULT_OCR_CONFIDENCE_THRESHOLD = 0.6


if __name__ == "__main__":
    # Test type definitions
    p = Point(100, 200)
    print(f"✓ Point created: {p}")

    r = Rect(10, 20, 100, 50)
    print(f"✓ Rect created: {r}")
    print(f"  Center: {r.center()}")
    print(f"  Contains {p}: {r.contains(p)}")

    print(f"✓ ElementType.CARD: {ElementType.CARD.value}")
    print(f"✓ ActionType.CLICK: {ActionType.CLICK.value}")
    print(f"✓ CardState.IN_SLOT: {CardState.IN_SLOT.value}")
    print(f"✓ Blacklisted keys: {BLACKLISTED_KEYS}")
    print("\n✓ All type definitions loaded successfully")
