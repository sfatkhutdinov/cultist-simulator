# Learning Library Contract

**Library**: `learning_lib`  
**Purpose**: RL agent, knowledge base, strategy evolution, and performance tracking  
**Dependencies**: Stable-Baselines3, SQLite, NumPy

---

## Public Interface

### Agent Functions

#### `select_action(game_state: GameState) -> Action`
Chooses next action based on current game state and learned policy.

**Input**: GameState object  
**Output**: Action object (click, drag, key_press, or wait)  
**Performance**: <500ms (NFR-001)  
**Errors**: `ModelNotLoadedError`, `StateProcessingError`

#### `update_knowledge(state: GameState, action: Action, next_state: GameState, reward: float) -> None`
Updates agent's knowledge from experience tuple.

**Input**: SARS tuple (state, action, reward, next_state)  
**Output**: None (updates internal knowledge base)  
**Performance**: <100ms (NFR-003)

#### `detect_loop(action_history: List[Action], window_size: int = 30) -> bool`
Identifies repetitive action patterns (FR-018, NFR-006).

**Input**: Recent action history, window size for comparison  
**Output**: True if loop detected  
**Performance**: <10ms

### Knowledge Base Functions

#### `query_knowledge(query_type: str, parameters: dict) -> QueryResult`
Retrieves relevant knowledge from database.

**Input**: Query type (e.g., "similar_states", "mechanic", "strategy")  
**Output**: QueryResult with matching records  
**Performance**: <100ms (NFR-003)

#### `store_session(session: Session) -> str`
Persists complete session recording.

**Input**: Session object with all states, actions, outcomes  
**Output**: Session ID  
**Performance**: <1000ms (batch write)

### CLI Interface

```bash
learning_lib --select-action state.json [--output action.json]
learning_lib --query-knowledge --type similar_states --params '{"state_hash":"abc123"}'
learning_lib --train --episodes 100 [--checkpoint-interval 10]
learning_lib --articulate-strategy [--agent-id agent_001]
learning_lib --metrics [--agent-id agent_001] [--last-n 50]
```

---

## Data Contracts

### Action Selection Request/Response
Request: GameState JSON  
Response: 
```python
{
    "action_type": "click" | "drag" | "key_press" | "wait",
    "parameters": {...},
    "confidence": float,
    "expected_reward": float,
    "strategy_reasoning": "why this action was chosen"
}
```

### Knowledge Query Result
```python
{
    "query_type": str,
    "results": [...],  # List of matching records
    "result_count": int,
    "query_time_ms": float
}
```

---

## Testing Requirements

1. `test_select_action_within_time_budget()` - Performance (500ms)
2. `test_loop_detection_identifies_repetition()` - Loop detection (FR-018)
3. `test_knowledge_query_fast()` - Query performance (<100ms)
4. `test_session_storage_preserves_data()` - Persistence (NFR-005)
5. `test_improvement_over_episodes()` - Learning validation (FR-024)

---

## Configuration

```python
learning_config = {
    "algorithm": "PPO",
    "model_path": "models/agent.zip",
    "knowledge_db": "data/knowledge_base.db",
    "exploration_rate": 0.1,
    "loop_detection_window": 30,
    "loop_similarity_threshold": 0.8
}
```
