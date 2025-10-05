# Learning API

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

**Module**: `src.learning`  
**Generated**: 2025-10-04 22:36:32

---

## Table of Contents

- [Functions](#functions)
- [Classes](#classes)

---

## Functions


### `detect_loop(action_history: List[Any], window_size: int = 30) -> bool`

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

---

### `get_logger(name: str = None)`

Get a logger instance.

Args:
    name: Optional logger name (typically __name__)

Returns:
    Structlog logger instance

---

### `query_knowledge(query_type: str, parameters: Dict[str, Any]) -> src.learning.QueryResult`

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

---

### `select_action(game_state: Optional[src.lib.types.GameState]) -> src.lib.types.Action`

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

---

### `store_session(session: Union[src.lib.types.Session, Dict[str, Any], NoneType]) -> str`

Store a complete session in the knowledge base.

T096: Session persistence for later analysis and training.

Args:
    session: Session object or dict to persist
    
Returns:
    Session ID (UUID string or session_id from dict)
    
Raises:
    KnowledgeBaseError: If storage fails
    ValueError: If session is None

---

### `update_knowledge(state: Optional[Any], action: Optional[Any], next_state: Optional[Any], reward: float) -> None`

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

---

## Classes


### `class Action`

Represents an action to be performed by the agent.
T041: Implement Action entity.

**Methods:**


#### `__init__(self, action_type: src.lib.types.ActionType, parameters: Dict[str, Any], timestamp: datetime.datetime = <factory>, metadata: Dict[str, Any] = <factory>) -> None`

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

### `class KnowledgeBase`

SQLite-based knowledge base for agent learning.

Stores:
- Sessions: Complete gameplay episodes
- Experiences: SARS tuples for training
- Mechanics: Learned game rules
- Strategies: Successful action sequences

**Methods:**


#### `__init__(self, db_path: Optional[str] = None)`

Initialize knowledge base connection.

Args:
    db_path: Path to SQLite database (default: data/knowledge_base.db)


#### `close(self) -> None`

Close database connection.


#### `get_mechanic(self, mechanic_name: str) -> Optional[Dict[str, Any]]`

Retrieve a learned mechanic by name.


#### `list_mechanics(self) -> List[Dict[str, Any]]`

List all learned mechanics.


#### `store_experience(self, state: Any, action: Any, next_state: Any, reward: float) -> None`

Store a single experience tuple (SARS).

Args:
    state: Current game state
    action: Action taken
    next_state: Resulting game state
    reward: Reward received


#### `store_mechanic(self, mechanic_name: str, data: Dict[str, Any]) -> None`

Store a learned game mechanic.
T098: Implement store_mechanic() for game rules.

Args:
    mechanic_name: Name/identifier for the mechanic
    data: Dictionary containing mechanic data (description, conditions, effects, etc.)

---

### `class KnowledgeBaseError`

Raised when knowledge base operation fails.

---

### `class MetricsTracker`

Tracks and aggregates performance metrics across sessions.

**Methods:**


#### `__init__(self, storage_path: str = 'data/metrics.json')`

Initialize metrics tracker.


#### `clear_metrics(self) -> None`

Clear all metrics.


#### `get_aggregate_stats(self, last_n: Optional[int] = None) -> Dict[str, Any]`

Get aggregated statistics.

Args:
    last_n: Only consider last N sessions (None = all)

Returns:
    Dictionary of aggregate statistics


#### `get_recent_performance(self, window: int = 10) -> Dict[str, Any]`

Get performance over recent sessions.


#### `has_improved(self, window: int = 10, baseline_window: int = 100) -> bool`

Check if agent has improved over time.

Args:
    window: Recent sessions to compare
    baseline_window: Baseline sessions for comparison
    
Returns:
    True if recent performance exceeds baseline


#### `record_metric(self, metric: src.learning.metrics.PerformanceMetric) -> None`

Record a new performance metric.

---

### `class ModelNotLoadedError`

Raised when RL model is not loaded/trained.

---

### `class QueryResult`

Result from knowledge base query.

**Methods:**


#### `__init__(self, result_count: int, query_time_ms: float, results: List[Any], metadata: Dict[str, Any]) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class Session`

Represents a complete game session.
T043: Implement Session entity.

**Methods:**


#### `__init__(self, session_id: str, agent_id: str, start_time: datetime.datetime, end_time: Optional[datetime.datetime] = None, end_condition: Optional[src.lib.types.EndCondition] = None, total_actions: int = 0, total_reward: float = 0.0, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class StrategyManager`

Manages strategy CRUD operations and evolution.
T100, T101: Strategy entity operations and evolution.

**Methods:**


#### `__init__(self, storage_path: str = 'data/strategies.json')`

Initialize strategy manager.


#### `create_strategy(self, strategy_id: str, parameters: Dict[str, Any]) -> src.learning.strategy.Strategy`

Create a new strategy.


#### `delete_strategy(self, strategy_id: str) -> bool`

Delete a strategy.


#### `evolve_strategy(self, base_strategy_id: str, mutation_rate: float = 0.1) -> Optional[src.learning.strategy.Strategy]`

Create a mutated version of a strategy.
T101: Strategy evolution through mutation.


#### `get_strategy(self, strategy_id: str) -> Optional[src.learning.strategy.Strategy]`

Get a strategy by ID.


#### `list_strategies(self) -> List[src.learning.strategy.Strategy]`

List all strategies.


#### `load_strategy(self, strategy_id: str) -> Optional[src.learning.strategy.Strategy]`

Load a strategy by ID (alias for get_strategy).


#### `merge_strategies(self, strategy_id_1: str | src.learning.strategy.Strategy, strategy_id_2: str | src.learning.strategy.Strategy, weight: float = 0.5) -> Optional[src.learning.strategy.Strategy]`

Merge two strategies with weighted averaging.
T101: Strategy evolution through merging.
Accepts either strategy IDs (str) or Strategy objects.


#### `mutate_strategy(self, strategy: src.learning.strategy.Strategy, mutation_rate: float = 0.1) -> src.learning.strategy.Strategy`

Mutate a strategy (alias for testing compatibility).


#### `save_strategy(self, strategy: src.learning.strategy.Strategy) -> None`

Save a strategy to the manager.


#### `update_performance(self, strategy_id: str, won: bool = False, survival_time: float = 0.0) -> Optional[src.learning.strategy.Strategy]`

Update strategy performance metrics after an episode.

Args:
    strategy_id: The strategy to update
    won: Whether the episode was won
    survival_time: How long the agent survived

Returns:
    Updated strategy or None if not found


#### `update_strategy(self, strategy_id: str, **kwargs) -> Optional[src.learning.strategy.Strategy]`

Update strategy attributes.

---
