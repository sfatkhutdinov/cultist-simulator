# Lib.Types API

Shared type definitions for Cultist Simulator AI Agent.
Provides common data structures used across all libraries.

**Module**: `src.lib.types`  
**Generated**: 2025-10-04 22:36:32

---

## Table of Contents

- [Functions](#functions)
- [Classes](#classes)

---


## Classes


### `class Action`

Represents an action to be performed by the agent.
T041: Implement Action entity.

**Methods:**


#### `__init__(self, action_type: src.lib.types.ActionType, parameters: Dict[str, Any], timestamp: datetime.datetime = <factory>, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class ActionResult`

Result from executing an automation action.

**Methods:**


#### `__init__(self, success: bool, safety_validated: bool, blocked_reason: Optional[str] = None, duration_ms: Optional[float] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class ActionType`

Types of actions the agent can perform.

---

### `class Agent`

Represents the AI agent configuration and state.
T044: Implement Agent entity.

**Methods:**


#### `__init__(self, agent_id: str, name: str, created_at: datetime.datetime, total_sessions: int = 0, total_actions: int = 0, learning_rate: float = 0.001, exploration_rate: float = 0.1, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class Card`

Represents a card in Cultist Simulator.
T042: Implement Card entity.

**Methods:**


#### `__init__(self, card_id: str, name: str, card_type: str, state: src.lib.types.CardState, position: Optional[src.lib.types.Point] = None, slot_id: Optional[str] = None, decay_timer: Optional[float] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class CardState`

Possible states of a game card.

---

### `class ConstraintType`

Types of safety constraints.

---

### `class ElementType`

Types of game elements that can be detected.

---

### `class EndCondition`

How a game session ended.

---

### `class ExecutionResult`

Result of an action execution.

**Methods:**


#### `__init__(self, success: bool, status: src.lib.types.ExecutionStatus, message: Optional[str] = None, execution_time_ms: Optional[float] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class ExecutionStatus`

Status of action execution.

---

### `class GameElement`

Represents a detected UI element in the game.
T040: Implement GameElement entity.

**Methods:**


#### `__init__(self, element_type: src.lib.types.ElementType, bounds: src.lib.types.Rect, confidence: float, text: Optional[str] = None, state: Optional[str] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class GameState`

Complete snapshot of the game state at a point in time.
T039: Implement GameState entity.

**Methods:**


#### `__init__(self, timestamp: datetime.datetime, window_bounds: src.lib.types.Rect, elements: List[src.lib.types.GameElement], text_regions: List[src.lib.types.TextRegion], screenshot: Optional[numpy.ndarray] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.


#### `from_dict(data: Dict[str, Any]) -> 'GameState'`

Deserialize GameState from dictionary (T123).


#### `to_dict(self) -> Dict[str, Any]`

Serialize GameState to dictionary (T123).

---

### `class Goal`

Extracted goal from narrative text.

**Methods:**


#### `__init__(self, description: str, confidence: float, goal_type: Optional[str] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class MetricType`

Types of performance metrics tracked.

---

### `class MouseButton`

Mouse button identifiers.

---

### `class Narrative`

A narrative sequence with semantic embedding.

**Methods:**


#### `__init__(self, narrative_id: str, text: str, embedding: Optional[numpy.ndarray] = None, session_id: Optional[str] = None, timestamp: Optional[datetime.datetime] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class PerformanceMetric`

Represents a performance metric tracked over time.
T046: Implement PerformanceMetric entity.

**Methods:**


#### `__init__(self, metric_type: src.lib.types.MetricType, value: float, timestamp: datetime.datetime, session_id: Optional[str] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class Point`

A 2D point representing screen coordinates.

**Methods:**


#### `__init__(self, x: int, y: int) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class QueryResult`

Result of a knowledge base query.

**Methods:**


#### `__init__(self, results: List[Dict[str, Any]], result_count: int, query_time_ms: float, metadata: Dict[str, Any] = <factory>) -> None`

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

### `class Session`

Represents a complete game session.
T043: Implement Session entity.

**Methods:**


#### `__init__(self, session_id: str, agent_id: str, start_time: datetime.datetime, end_time: Optional[datetime.datetime] = None, end_condition: Optional[src.lib.types.EndCondition] = None, total_actions: int = 0, total_reward: float = 0.0, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class Strategy`

Represents a learned strategy for achieving goals.
T045: Implement Strategy entity.

**Methods:**


#### `__init__(self, strategy_id: str, name: str, goal: str, action_sequence: List[str], success_rate: float, times_used: int = 0, avg_reward: float = 0.0, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class TextAnalysis`

Result of NLP text analysis.

**Methods:**


#### `__init__(self, text: str, embedding: Optional[numpy.ndarray] = None, sentiment: Optional[str] = None, entities: List[str] = <factory>, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class TextRegion`

Represents a region of text extracted from the game screen.

**Methods:**


#### `__init__(self, text: str, bounds: src.lib.types.Rect, confidence: float) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class ValidationResult`

Result of a safety validation check.

**Methods:**


#### `__init__(self, is_allowed: bool, reason: Optional[str] = None, constraints_violated: List[src.lib.types.ConstraintType] = <factory>, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---
