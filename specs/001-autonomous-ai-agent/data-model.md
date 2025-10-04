# Data Model

**Feature**: Autonomous AI Agent for Cultist Simulator  
**Date**: 2025-10-04  
**Phase**: 1 - Data Design

## Core Entities

### Agent
The autonomous AI system that learns to play the game.

**Attributes**:
- `agent_id`: str (UUID) - Unique identifier
- `created_at`: datetime - Creation timestamp
- `strategy_version`: int - Current strategy iteration
- `total_episodes`: int - Cumulative episodes played
- `knowledge_base_ref`: str - Reference to knowledge database
- `model_checkpoint_path`: str - Path to saved RL model
- `config`: dict - Agent configuration (hyperparameters, settings)

**State**:
- `current_episode_id`: str | None - Active episode reference
- `is_running`: bool - Whether agent is currently playing
- `last_action_time`: datetime - Timestamp of last action
- `exploration_rate`: float - Current exploration vs. exploitation balance

**Behaviors**:
- `select_action(game_state) -> Action` - Choose next action based on observations
- `update_knowledge(observation, reward) -> None` - Learn from experience
- `detect_loop(action_history) -> bool` - Identify repetitive patterns
- `articulate_strategy() -> str` - Explain current approach in human-readable form

**Persistence**: SQLite `agents` table + model checkpoint files

---

### GameState
A snapshot of the Cultist Simulator game at a point in time.

**Attributes**:
- `state_id`: str (UUID) - Unique identifier
- `timestamp`: datetime - When state was captured
- `episode_id`: str - Parent episode reference
- `screenshot_path`: str | None - Path to saved screenshot (optional)

**Visual Elements**:
- `detected_elements`: List[GameElement] - All identified UI components
- `window_bounds`: Rect - Game window position and size
- `has_focus`: bool - Whether game window is active

**Extracted Data**:
- `resources`: dict[str, float] - Numerical values (health, funds, time, etc.)
- `cards`: List[Card] - All visible cards with states
- `timers`: List[Timer] - Active countdowns
- `narrative_text`: List[NarrativeText] - Detected text elements
- `available_actions`: List[str] - Possible interactions identified

**Derived State**:
- `is_game_over`: bool - Whether terminal state detected
- `is_win_state`: bool | None - Win condition detected (None if unknown)
- `game_phase`: str - Estimated phase (early_game, mid_game, end_game)

**Behaviors**:
- `diff(other: GameState) -> StateChanges` - Compare to another state
- `serialize() -> dict` - Convert to JSON-compatible dict
- `to_rl_observation() -> np.ndarray` - Convert to RL model input format

**Persistence**: JSON snapshots in `data/sessions/{episode_id}/states/`

---

### GameElement
An interactive component within the game.

**Attributes**:
- `element_id`: str - Unique identifier (hash of position + type)
- `element_type`: ElementType (enum) - card | button | slot | timer | text | other
- `bounding_box`: Rect - Screen coordinates
- `confidence`: float - Detection confidence (0-1)
- `visual_signature`: np.ndarray | None - Template or feature vector

**Element-Specific Data**:
- `label`: str | None - Text label if available
- `state`: str | None - State indicator (e.g., "active", "disabled", "highlighted")
- `icon_type`: str | None - Icon classification if applicable

**Behaviors**:
- `is_clickable() -> bool` - Whether element accepts click interactions
- `get_center() -> Point` - Center coordinates for clicking
- `matches_template(template) -> float` - Similarity score to reference

**Persistence**: Part of GameState JSON, not separately stored

---

### Card
Game card representation (specific type of GameElement).

**Attributes**:
- `card_id`: str - Unique identifier
- `card_type`: str - Category (aspect, follower, lore, etc.)
- `title`: str - Card name extracted via OCR
- `position`: Point - Current screen location
- `state`: CardState (enum) - in_hand | in_slot | dragging | decaying

**Extracted Properties**:
- `aspects`: List[str] - Card attributes/tags
- `description`: str | None - Card text (OCR'd)
- `quantity`: int - Stack size if applicable

**Behaviors**:
- `can_combine_with(other: Card) -> bool` - Check valid combinations
- `get_drag_path_to(target: Point) -> List[Point]` - Calculate drag trajectory

**Persistence**: Part of GameState, indexed in knowledge base for pattern recognition

---

### Action
A discrete interaction with the game.

**Attributes**:
- `action_id`: str (UUID) - Unique identifier
- `timestamp`: datetime - When action was executed
- `episode_id`: str - Parent episode reference
- `pre_state_id`: str - Game state before action
- `post_state_id`: str | None - Game state after action (None if pending)

**Action Details**:
- `action_type`: ActionType (enum) - click | drag | key_press | wait | composite
- `parameters`: dict - Action-specific params
  - For click: `{"x": int, "y": int, "button": str}`
  - For drag: `{"start": Point, "end": Point, "duration": float}`
  - For key: `{"key": str, "modifiers": List[str]}`
  - For wait: `{"duration": float}`
  - For composite: `{"sub_actions": List[Action]}`

**Safety Validation**:
- `is_validated`: bool - Passed safety checks
- `validation_result`: ValidationResult | None - Safety check details
- `was_blocked`: bool - Whether action was prevented

**Outcome**:
- `execution_status`: str - success | failed | blocked | timeout
- `observed_changes`: StateChanges | None - Detected state transitions
- `reward_signal`: float | None - Reward assigned by learning system

**Behaviors**:
- `validate_safety(window_bounds, blacklist) -> ValidationResult` - Check constraints
- `execute(automation_lib) -> ExecutionResult` - Perform the action
- `estimate_duration() -> float` - Predicted execution time

**Persistence**: SQLite `actions` table + linked to session recordings

---

### Session
A complete playthrough from game start to end condition.

**Attributes**:
- `session_id`: str (UUID) - Unique identifier
- `agent_id`: str - Which agent played this session
- `start_time`: datetime - Session start
- `end_time`: datetime | None - Session end (None if ongoing)
- `random_seed`: int - RNG seed for reproducibility

**Episode Data**:
- `game_states`: List[str] - Ordered state IDs
- `actions_taken`: List[str] - Ordered action IDs
- `total_actions`: int - Count of actions
- `duration_seconds`: float - Wall-clock time

**Outcome**:
- `end_condition`: str - game_over | win | crash | manual_stop | timeout
- `win_type`: str | None - Specific win condition if applicable
- `survival_time_ingame`: float - In-game time survived
- `resources_at_end`: dict[str, float] - Final resource values

**Performance Metrics**:
- `unique_mechanics_discovered`: int - New patterns learned
- `loop_events`: int - Number of loop detections
- `safety_violations_blocked`: int - Blocked dangerous actions

**Behaviors**:
- `calculate_reward() -> float` - Compute episode reward signal
- `extract_patterns() -> List[Pattern]` - Identify reusable strategies
- `replay(speed_multiplier) -> Iterator[GameState]` - Replay session for analysis

**Persistence**: SQLite `sessions` table + full recording in `data/sessions/{session_id}/`

---

### KnowledgeBase
The agent's accumulated understanding.

**Attributes**:
- `kb_id`: str - Database identifier
- `agent_id`: str - Owner agent reference
- `created_at`: datetime - Creation time
- `last_updated`: datetime - Most recent modification
- `version`: int - Schema version for migrations

**Stored Knowledge**:
- `game_mechanics`: List[Mechanic] - Discovered rules
- `state_transitions`: List[Transition] - Cause-effect relationships
- `successful_strategies`: List[Strategy] - Winning approaches
- `failure_patterns`: List[Pattern] - Approaches that failed
- `narrative_embeddings`: dict[str, np.ndarray] - Text semantic vectors

**Mechanic**:
```python
{
  "mechanic_id": str,
  "description": str,  # e.g., "Combining health + passion creates vitality"
  "evidence_count": int,  # Number of observations
  "confidence": float,  # 0-1 belief in this rule
  "conditions": dict,  # Preconditions
  "effects": dict,  # Observed outcomes
  "discovered_session": str  # First observation
}
```

**Transition**:
```python
{
  "from_state_signature": str,  # State hash or feature vector
  "action_signature": str,  # Action hash
  "to_state_signature": str,  # Resulting state hash
  "probability": float,  # Observed frequency
  "reward": float,  # Average reward
  "observations": int  # Sample count
}
```

**Behaviors**:
- `query_similar_states(state: GameState) -> List[Transition]` - Find relevant history
- `update_mechanic(mechanic_id, new_evidence) -> None` - Refine understanding
- `prune_low_confidence(threshold) -> int` - Remove unreliable knowledge
- `export_to_json() -> dict` - Serialize for sharing/backup

**Persistence**: SQLite `knowledge_base.db` with tables for mechanics, transitions, strategies

---

### Strategy
A high-level approach to gameplay.

**Attributes**:
- `strategy_id`: str (UUID) - Unique identifier
- `name`: str - Human-readable strategy name
- `version`: int - Iteration number
- `created_from_session`: str | None - Session that spawned this strategy

**Strategy Definition**:
- `goal_priorities`: List[str] - Ordered list of objectives
  - Example: ["survive_60_minutes", "accumulate_funds", "explore_rituals"]
- `decision_rules`: List[Rule] - Conditional logic
  - Example: `{"if": "health < 3", "then": "prioritize_health_gain"}`
- `exploration_weight`: float - Exploration vs. exploitation balance
- `risk_tolerance`: float - Willingness to try uncertain actions

**Performance History**:
- `sessions_played`: int - Times this strategy was used
- `win_rate`: float - Success percentage
- `avg_survival_time`: float - Average performance
- `best_outcome`: dict - Best result achieved

**Evolution**:
- `parent_strategy_id`: str | None - Strategy this evolved from
- `mutations`: List[str] - Changes from parent
- `fitness_score`: float - Comparative performance metric

**Behaviors**:
- `select_goal(game_state) -> str` - Choose current objective
- `evaluate_action_alignment(action) -> float` - Score action fit
- `mutate(mutation_rate) -> Strategy` - Create variant for exploration
- `merge_with(other: Strategy) -> Strategy` - Combine successful elements

**Persistence**: SQLite `strategies` table + JSON config exports

---

### PerformanceMetric
Measurable indicator of agent progress.

**Attributes**:
- `metric_id`: str - Unique identifier
- `metric_type`: MetricType (enum) - win_rate | survival_time | resources | unique_endings | learning_rate
- `agent_id`: str - Owner agent
- `timestamp`: datetime - Measurement time

**Current Value**:
- `value`: float - Current metric value
- `unit`: str - Measurement unit (e.g., "seconds", "percentage", "count")

**Historical Data**:
- `rolling_avg_10`: float - Average over last 10 episodes
- `rolling_avg_50`: float - Average over last 50 episodes
- `rolling_avg_100`: float - Average over last 100 episodes
- `all_time_best`: float - Peak value ever achieved
- `all_time_worst`: float - Lowest value recorded

**Trend Analysis**:
- `trend_direction`: str - improving | declining | stable
- `trend_confidence`: float - Statistical confidence in trend
- `improvement_rate`: float - Rate of change per episode

**Behaviors**:
- `update(new_value) -> None` - Add new measurement and recalculate
- `get_trend(window_size) -> TrendData` - Analyze recent trajectory
- `to_timeseries() -> List[Tuple[datetime, float]]` - Export for plotting

**Persistence**: SQLite `metrics` table + aggregation views

---

### SafetyConstraint
A rule preventing agent actions outside game boundaries.

**Attributes**:
- `constraint_id`: str - Unique identifier
- `constraint_type`: ConstraintType (enum) - window_bounds | key_blacklist | focus_required | rate_limit
- `is_active`: bool - Whether constraint is enforced
- `priority`: int - Enforcement order (higher = checked first)

**Constraint Definition**:
- `validation_function`: str - Name of validation function
- `parameters`: dict - Constraint-specific config
  - window_bounds: `{"window_id": str, "margin": int}`
  - key_blacklist: `{"forbidden_keys": List[str]}`
  - focus_required: `{"window_id": str}`
  - rate_limit: `{"max_actions_per_second": float}`

**Enforcement History**:
- `total_checks`: int - Number of validations performed
- `total_blocks`: int - Number of actions prevented
- `last_violation`: datetime | None - Most recent block
- `violation_log`: List[dict] - Recent violation details

**Behaviors**:
- `validate(action, context) -> ValidationResult` - Check if action allowed
- `log_violation(action, reason) -> None` - Record blocked action
- `get_violation_rate() -> float` - Percentage of blocked actions

**Persistence**: SQLite `safety_constraints` table + violation logs

---

## Enumerations

### ElementType
```python
class ElementType(Enum):
    CARD = "card"
    BUTTON = "button"
    SLOT = "slot"
    TIMER = "timer"
    TEXT = "text"
    ICON = "icon"
    OTHER = "other"
```

### ActionType
```python
class ActionType(Enum):
    CLICK = "click"
    DRAG = "drag"
    KEY_PRESS = "key_press"
    WAIT = "wait"
    COMPOSITE = "composite"
```

### CardState
```python
class CardState(Enum):
    IN_HAND = "in_hand"
    IN_SLOT = "in_slot"
    DRAGGING = "dragging"
    DECAYING = "decaying"
    HIDDEN = "hidden"
```

### MetricType
```python
class MetricType(Enum):
    WIN_RATE = "win_rate"
    SURVIVAL_TIME = "survival_time"
    RESOURCES_ACCUMULATED = "resources_accumulated"
    UNIQUE_ENDINGS = "unique_endings"
    LEARNING_RATE = "learning_rate"
    ACTIONS_PER_MINUTE = "actions_per_minute"
```

### ConstraintType
```python
class ConstraintType(Enum):
    WINDOW_BOUNDS = "window_bounds"
    KEY_BLACKLIST = "key_blacklist"
    FOCUS_REQUIRED = "focus_required"
    RATE_LIMIT = "rate_limit"
    EXIT_PREVENTION = "exit_prevention"
```

---

## Value Objects

### Point
```python
@dataclass
class Point:
    x: int
    y: int
```

### Rect
```python
@dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int
    
    def contains(self, point: Point) -> bool: ...
    def center(self) -> Point: ...
```

### StateChanges
```python
@dataclass
class StateChanges:
    added_elements: List[GameElement]
    removed_elements: List[GameElement]
    moved_elements: List[Tuple[GameElement, Point]]
    resource_changes: dict[str, float]
    new_narrative_text: List[str]
```

### ValidationResult
```python
@dataclass
class ValidationResult:
    is_valid: bool
    constraint_violations: List[str]
    warnings: List[str]
    corrected_action: Action | None  # If action can be auto-corrected
```

---

## Relationships

```
Agent 1 ─── * Session (plays many sessions)
Agent 1 ─── 1 KnowledgeBase (has one knowledge base)
Agent 1 ─── * Strategy (evolves multiple strategies)
Agent 1 ─── * PerformanceMetric (tracks multiple metrics)

Session 1 ─── * GameState (contains many states)
Session 1 ─── * Action (contains many actions)
Session 1 ─── 1 Agent (played by one agent)

GameState 1 ─── * GameElement (contains many elements)
GameState 1 ─── * Card (contains many cards - subset of elements)

Action N ─── 1 GameState (pre-state)
Action N ─── 1 GameState (post-state, optional)
Action N ─── * SafetyConstraint (validated against many constraints)

KnowledgeBase 1 ─── * Mechanic (stores many mechanics)
KnowledgeBase 1 ─── * Transition (stores many transitions)
KnowledgeBase 1 ─── * Strategy (evolves strategies)

Strategy 1 ─── * Session (used in many sessions)
Strategy N ─── 1 Strategy (parent, optional for evolved strategies)
```

---

## Storage Schema (SQLite)

### agents
```sql
CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    strategy_version INTEGER,
    total_episodes INTEGER,
    knowledge_base_ref TEXT,
    model_checkpoint_path TEXT,
    config JSON
);
```

### sessions
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    agent_id TEXT REFERENCES agents(agent_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    random_seed INTEGER,
    end_condition TEXT,
    win_type TEXT,
    survival_time_ingame REAL,
    resources_at_end JSON,
    total_actions INTEGER,
    duration_seconds REAL,
    unique_mechanics_discovered INTEGER,
    loop_events INTEGER,
    safety_violations_blocked INTEGER
);
CREATE INDEX idx_sessions_agent ON sessions(agent_id);
CREATE INDEX idx_sessions_end_condition ON sessions(end_condition);
```

### actions
```sql
CREATE TABLE actions (
    action_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP,
    episode_id TEXT REFERENCES sessions(session_id),
    pre_state_id TEXT,
    post_state_id TEXT,
    action_type TEXT,
    parameters JSON,
    is_validated BOOLEAN,
    was_blocked BOOLEAN,
    execution_status TEXT,
    reward_signal REAL
);
CREATE INDEX idx_actions_episode ON actions(episode_id);
CREATE INDEX idx_actions_type ON actions(action_type);
```

### mechanics
```sql
CREATE TABLE mechanics (
    mechanic_id TEXT PRIMARY KEY,
    kb_id TEXT,
    description TEXT,
    evidence_count INTEGER,
    confidence REAL,
    conditions JSON,
    effects JSON,
    discovered_session TEXT REFERENCES sessions(session_id)
);
CREATE INDEX idx_mechanics_confidence ON mechanics(confidence);
```

### strategies
```sql
CREATE TABLE strategies (
    strategy_id TEXT PRIMARY KEY,
    name TEXT,
    version INTEGER,
    created_from_session TEXT REFERENCES sessions(session_id),
    goal_priorities JSON,
    decision_rules JSON,
    exploration_weight REAL,
    risk_tolerance REAL,
    sessions_played INTEGER,
    win_rate REAL,
    avg_survival_time REAL,
    parent_strategy_id TEXT REFERENCES strategies(strategy_id)
);
```

### metrics
```sql
CREATE TABLE metrics (
    metric_id TEXT PRIMARY KEY,
    metric_type TEXT,
    agent_id TEXT REFERENCES agents(agent_id),
    timestamp TIMESTAMP,
    value REAL,
    unit TEXT,
    rolling_avg_10 REAL,
    rolling_avg_50 REAL,
    rolling_avg_100 REAL
);
CREATE INDEX idx_metrics_agent_type ON metrics(agent_id, metric_type);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);
```

### safety_constraints
```sql
CREATE TABLE safety_constraints (
    constraint_id TEXT PRIMARY KEY,
    constraint_type TEXT,
    is_active BOOLEAN,
    priority INTEGER,
    validation_function TEXT,
    parameters JSON,
    total_checks INTEGER,
    total_blocks INTEGER,
    last_violation TIMESTAMP
);
```

---

## Data Flow

1. **Game State Capture**:
   ```
   Game Window → Vision Lib → GameState → JSON Snapshot
   ```

2. **Action Selection**:
   ```
   GameState → Agent.select_action() → Action → Safety Validation → Automation Lib
   ```

3. **Knowledge Update**:
   ```
   (GameState, Action, Reward) → Agent.update_knowledge() → KnowledgeBase → SQLite
   ```

4. **Session Recording**:
   ```
   Start → GameState[] + Action[] → End → Session → SQLite + JSON Archive
   ```

5. **Metrics Tracking**:
   ```
   Session End → calculate_metrics() → PerformanceMetric.update() → SQLite + Tensorboard
   ```

---

## Data Lifecycle

1. **Creation**: Game states captured every action cycle (~500ms)
2. **Processing**: Immediate analysis for action selection
3. **Storage**: 
   - Hot data: In-memory for current session
   - Warm data: SQLite for recent sessions (last 100)
   - Cold data: JSON archives for older sessions
4. **Archival**: Sessions older than 30 days compressed to JSON.gz
5. **Retention**: Keep all data indefinitely (disk is cheap, learning is valuable)

---

## Performance Considerations

- **In-Memory Caching**: Current game state, recent actions, active strategy
- **Lazy Loading**: Load historical sessions only when needed for analysis
- **Index Optimization**: Database indices on high-query fields
- **Batch Writes**: Buffer metrics updates, write at episode end
- **Embedding Cache**: Store computed NLP embeddings to avoid recomputation
