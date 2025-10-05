"""
Shared type definitions for Cultist Simulator AI Agent.
Provides common data structures used across all libraries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import numpy as np


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
        return Point(x=self.x + self.width // 2, y=self.y + self.height // 2)

    def contains(self, point: Point) -> bool:
        """Check if a point is inside the rectangle."""
        return (
            self.x <= point.x <= self.x + self.width
            and self.y <= point.y <= self.y + self.height
        )

    def __str__(self) -> str:
        return f"Rect(x={self.x}, y={self.y}, w={self.width}, h={self.height})"


@dataclass
class ActionResult:
    """Result from executing an automation action."""

    success: bool
    safety_validated: bool
    blocked_reason: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


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
    # macOS dangerous combinations
    "cmd+q",  # Quit application
    "cmd+w",  # Close window
    "cmd+tab",  # Switch application
    "cmd+`",  # Switch window
    "cmd+option+q",  # Force quit (multiple modifiers)
    "cmd+option+shift+q",  # Force quit with more modifiers
    "cmd+shift+q",  # Log out
    # Windows dangerous combinations
    "alt+f4",  # Close window/app
    "ctrl+shift+escape",  # Task manager
    "ctrl+alt+delete",  # System interrupt
    # Generic dangerous keys
    "escape",  # Often used for menus that could exit
    "f4",  # Potential Alt+F4 key
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

# Display parameters (for testing/fallback)
DEFAULT_SCREEN_WIDTH = 1920
DEFAULT_SCREEN_HEIGHT = 1080

# Time conversion constants
MS_PER_SECOND = 1000.0


# ============================================================================
# Entity Classes
# ============================================================================


@dataclass
class GameElement:
    """
    Represents a detected UI element in the game.
    T040: Implement GameElement entity.
    """

    element_type: ElementType
    bounds: Rect
    confidence: float
    text: Optional[str] = None
    state: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def center(self) -> Point:
        """Get the center point of the element."""
        return self.bounds.center()

    def __str__(self) -> str:
        return f"GameElement({self.element_type.value}, {self.bounds}, conf={self.confidence:.2f})"


@dataclass
class TextRegion:
    """Represents a region of text extracted from the game screen."""

    text: str
    bounds: Rect
    confidence: float

    def __str__(self) -> str:
        return f"TextRegion('{self.text[:20]}...', conf={self.confidence:.2f})"


@dataclass
class GameState:
    """
    Complete snapshot of the game state at a point in time.
    T039: Implement GameState entity.
    """

    timestamp: datetime
    window_bounds: Rect
    elements: List[GameElement]
    text_regions: List[TextRegion]
    screenshot: Optional[np.ndarray] = None  # Raw image data
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"GameState({len(self.elements)} elements, {len(self.text_regions)} text regions, {self.timestamp})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize GameState to dictionary (T123)."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "window_bounds": {
                "x": self.window_bounds.x,
                "y": self.window_bounds.y,
                "width": self.window_bounds.width,
                "height": self.window_bounds.height,
            },
            "elements": [
                {
                    "element_type": e.element_type.value,
                    "bounds": {
                        "x": e.bounds.x,
                        "y": e.bounds.y,
                        "width": e.bounds.width,
                        "height": e.bounds.height,
                    },
                    "confidence": e.confidence,
                    "text": e.text,
                    "state": e.state,
                    "metadata": e.metadata,
                }
                for e in self.elements
            ],
            "text_regions": [
                {
                    "text": t.text,
                    "bounds": {
                        "x": t.bounds.x,
                        "y": t.bounds.y,
                        "width": t.bounds.width,
                        "height": t.bounds.height,
                    },
                    "confidence": t.confidence,
                }
                for t in self.text_regions
            ],
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GameState":
        """Deserialize GameState from dictionary (T123)."""
        return GameState(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            window_bounds=Rect(**data["window_bounds"]),
            elements=[
                GameElement(
                    element_type=ElementType(e["element_type"]),
                    bounds=Rect(**e["bounds"]),
                    confidence=e["confidence"],
                    text=e.get("text"),
                    state=e.get("state"),
                    metadata=e.get("metadata", {}),
                )
                for e in data["elements"]
            ],
            text_regions=[
                TextRegion(
                    text=t["text"],
                    bounds=Rect(**t["bounds"]),
                    confidence=t["confidence"],
                )
                for t in data["text_regions"]
            ],
            metadata=data.get("metadata", {}),
        )


@dataclass
class Action:
    """
    Represents an action to be performed by the agent.
    T041: Implement Action entity.
    """

    action_type: ActionType
    parameters: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        params_str = ", ".join(f"{k}={v}" for k, v in list(self.parameters.items())[:2])
        return f"Action({self.action_type.value}, {params_str})"


@dataclass
class Card:
    """
    Represents a card in Cultist Simulator.
    T042: Implement Card entity.
    """

    card_id: str
    name: str
    card_type: str  # aspect, verb, resource, etc.
    state: CardState
    position: Optional[Point] = None
    slot_id: Optional[str] = None
    decay_timer: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Card({self.name}, {self.state.value})"


@dataclass
class Session:
    """
    Represents a complete game session.
    T043: Implement Session entity.
    """

    session_id: str
    agent_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    end_condition: Optional[EndCondition] = None
    total_actions: int = 0
    total_reward: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate session duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __str__(self) -> str:
        status = (
            "active"
            if self.end_time is None
            else f"ended ({self.end_condition.value if self.end_condition else 'unknown'})"
        )
        return f"Session({self.session_id}, {status}, {self.total_actions} actions)"


@dataclass
class Agent:
    """
    Represents the AI agent configuration and state.
    T044: Implement Agent entity.
    """

    agent_id: str
    name: str
    created_at: datetime
    total_sessions: int = 0
    total_actions: int = 0
    learning_rate: float = 0.001
    exploration_rate: float = 0.1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Agent({self.name}, {self.total_sessions} sessions, {self.total_actions} actions)"


@dataclass
class Strategy:
    """
    Represents a learned strategy for achieving goals.
    T045: Implement Strategy entity.
    """

    strategy_id: str
    name: str
    goal: str
    action_sequence: List[str]  # JSON-encoded actions
    success_rate: float
    times_used: int = 0
    avg_reward: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Strategy({self.name}, success={self.success_rate:.1%}, used={self.times_used})"


@dataclass
class PerformanceMetric:
    """
    Represents a performance metric tracked over time.
    T046: Implement PerformanceMetric entity.
    """

    metric_type: MetricType
    value: float
    timestamp: datetime
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Metric({self.metric_type.value}={self.value:.2f}, {self.timestamp})"


@dataclass
class ValidationResult:
    """Result of a safety validation check."""

    is_allowed: bool
    reason: Optional[str] = None
    constraints_violated: List[ConstraintType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def blocked_reason(self) -> Optional[str]:
        """Alias for reason (for test compatibility)."""
        return self.reason

    def __str__(self) -> str:
        status = "ALLOWED" if self.is_allowed else "BLOCKED"
        return f"ValidationResult({status}, {self.reason or 'no reason'})"


@dataclass
class ExecutionResult:
    """Result of an action execution."""

    success: bool
    status: ExecutionStatus
    message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"ExecutionResult({self.status.value}, {self.message or 'no message'})"


@dataclass
class QueryResult:
    """Result of a knowledge base query."""

    results: List[Dict[str, Any]]
    result_count: int
    query_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"QueryResult({self.result_count} results, {self.query_time_ms:.1f}ms)"


@dataclass
class TextAnalysis:
    """Result of NLP text analysis."""

    text: str
    embedding: Optional[np.ndarray] = None
    sentiment: Optional[str] = None  # positive, negative, neutral
    entities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"TextAnalysis('{self.text[:30]}...', sentiment={self.sentiment})"


@dataclass
class Goal:
    """Extracted goal from narrative text."""

    description: str
    confidence: float
    goal_type: Optional[str] = None  # ritual, resource, exploration, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Goal({self.description}, conf={self.confidence:.2f})"


@dataclass
class Narrative:
    """A narrative sequence with semantic embedding."""

    narrative_id: str
    text: str
    embedding: Optional[np.ndarray] = None
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Narrative({self.narrative_id}, '{self.text[:30]}...')"


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
