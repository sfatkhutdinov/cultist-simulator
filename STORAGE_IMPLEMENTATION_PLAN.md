# Storage System Implementation - Complete Fixes

## ✅ What's Been Implemented

### 1. Full Database Schema ✅
**File**: `src/learning/knowledge_base.py`

**New Tables**:
- `episodes` - Episode metadata (agent_id, start_time, total_actions, outcome)
- `game_states` - Captured states (screenshot_path, ocr_text, elements, bounds)
- `actions` - Actions taken (type, parameters, success, execution_time)
- `experiences` - SARS tuples (state, action, reward, next_state)
- `mechanics` - Learned rules (enhanced with confidence, observations)
- `patterns` - Discovered patterns (type, sequence, frequency, success_rate)

**New Methods**:
- `start_episode(agent_id)` → Returns episode_id
- `end_episode(episode_id, outcome)`
- `store_game_state(episode_id, state, screenshot_path)` → Returns state_id
- `store_action(episode_id, state_id, action, success, execution_time)` → Returns action_id
- `store_experience(episode_id, state_id, action_id, next_state_id, reward)` → Returns experience_id
- `get_episode_stats(episode_id)` → Episode statistics
- `get_recent_episodes(agent_id, limit)` → Recent episodes
- `get_total_experiences()` → Count of experiences
- `vacuum()` → Compact database

### 2. Storage Configuration ✅
**File**: `config/storage.yaml`

**Settings**:
- Database enable/disable
- Screenshot saving (interval, format, quality)
- Log rotation and archival
- TensorBoard retention
- Checkpoint retention
- Auto-cleanup policies
- Storage limits and warnings
- Performance tuning (batch size, commit interval)

### 3. Storage Manager ✅
**File**: `src/orchestrator/storage_manager.py`

**Features**:
- Automatic screenshot persistence
- Database storage coordination
- Log rotation and compression
- TensorBoard cleanup
- Checkpoint management
- Storage monitoring
- Configuration-driven behavior

**Methods**:
- `start_episode(agent_id)` - Initialize episode storage
- `end_episode(outcome)` - Finalize episode
- `store_state_action(state, action, screenshot, success, time)` - Store state+action
- `store_experience(state_id, action_id, next_state_id, reward)` - Store SARS
- `cleanup_old_data(dry_run)` - Automated cleanup
- `get_storage_info()` - Usage statistics

### 4. Data Management Tool ✅
**File**: `scripts/manage_data.py`

**Commands**:
- `info` - Show storage usage
- `clean-logs` - Archive old logs
- `clean-tensorboard` - Remove old runs
- `compact` - Vacuum database
- `clean-all` - Full cleanup

---

## 🔧 What Needs Integration

### Step 1: Integrate StorageManager into AgentRunner

**File to Modify**: `src/orchestrator/agent_runner.py`

**Changes Needed**:

1. **Import StorageManager**:
```python
from src.orchestrator.storage_manager import StorageManager
```

2. **Add to `__init__`**:
```python
def __init__(self, ...):
    # ... existing code ...
    
    # Initialize storage manager
    self.storage = StorageManager()
    logger.info("storage_manager_ready")
```

3. **Modify `_start_session`**:
```python
def _start_session(self) -> Session:
    # ... existing session creation ...
    
    # Start episode storage
    episode_id = self.storage.start_episode(self.agent_id)
    session.metadata['episode_id'] = episode_id
    
    return session
```

4. **Modify `_execute_step`** to store state/action:
```python
def _execute_step(self, session: Session) -> bool:
    # ... after action is selected and validated ...
    
    # Store state and action
    episode_id = session.metadata.get('episode_id')
    if episode_id:
        # Get screenshot if available
        screenshot = getattr(game_state, 'screenshot', None)
        
        # Store state + action
        state_id, action_id = self.storage.store_state_action(
            game_state,
            action,
            screenshot=screenshot,
            success=True,  # Will be updated after execution
            execution_time_ms=execution_time_ms
        )
        
        # Store IDs for later experience storage
        session.metadata['last_state_id'] = state_id
        session.metadata['last_action_id'] = action_id
    
    # ... execute action ...
```

5. **Add reward calculation and experience storage**:
```python
def _execute_step(self, session: Session) -> bool:
    # ... after action executed ...
    
    # Calculate reward (simple version)
    reward = self._calculate_reward(game_state, action, next_state)
    
    # Store experience
    if session.metadata.get('last_state_id') and session.metadata.get('last_action_id'):
        self.storage.store_experience(
            state_id=session.metadata['last_state_id'],
            action_id=session.metadata['last_action_id'],
            next_state_id=next_state_id,
            reward=reward
        )
```

6. **Modify `_end_session`**:
```python
def _end_session(self, session: Session, end_condition: EndCondition):
    # ... existing code ...
    
    # End episode storage
    outcome_map = {
        EndCondition.TIMEOUT: 'timeout',
        EndCondition.MANUAL_STOP: 'interrupted',
        EndCondition.CRASH: 'defeat',
        # Add more mappings
    }
    self.storage.end_episode(outcome=outcome_map.get(end_condition, 'completed'))
    
    # ... rest of existing code ...
```

7. **Add cleanup method**:
```python
def cleanup_storage(self):
    """Clean up old data based on retention policies."""
    stats = self.storage.cleanup_old_data(dry_run=False)
    logger.info("storage_cleaned", stats=stats)
    return stats
```

---

### Step 2: Integrate into Training Runner

**File to Modify**: `src/orchestrator/agent_runner.py` (TrainingRunner class)

**Changes Needed**:

1. **Add periodic cleanup**:
```python
def train(self, ...):
    # ... existing training loop ...
    
    # Run cleanup every 50 episodes
    if episode_num % 50 == 0:
        self.agent_runner.cleanup_storage()
```

2. **Add storage summary at end**:
```python
def train(self, ...):
    # ... after training completes ...
    
    # Show storage summary
    storage_info = self.agent_runner.storage.get_storage_info()
    print(f"\n📊 Storage Used: {storage_info['total_gb']:.2f} GB")
    print(f"   Database: {storage_info['database_bytes'] / (1024**2):.1f} MB")
    print(f"   Logs: {storage_info['logs_bytes'] / (1024**2):.1f} MB")
    
    # Get database stats
    if self.agent_runner.storage.kb:
        total_exp = self.agent_runner.storage.kb.get_total_experiences()
        print(f"\n📚 Experiences Collected: {total_exp:,}")
```

---

### Step 3: Add Reward Calculation

**File to Modify**: `src/orchestrator/agent_runner.py`

**New Method**:
```python
def _calculate_reward(
    self, 
    state: GameState, 
    action: Action, 
    next_state: GameState
) -> float:
    """
    Calculate reward for state transition.
    
    Simple heuristic for Phase 1:
    - +1.0 if new text appears (something changed)
    - +0.5 if action succeeded
    - -0.1 for each action (time cost)
    - -10.0 if episode ended (game over)
    """
    reward = 0.0
    
    # Time cost
    reward -= 0.1
    
    # Action success
    if action.metadata.get('success', True):
        reward += 0.5
    
    # State change detection
    if state.text_regions and next_state.text_regions:
        if len(next_state.text_regions) > len(state.text_regions):
            reward += 1.0  # New content appeared
    
    # Game over detection (simple heuristic)
    if next_state.text_regions:
        text = ' '.join([tr.text.lower() for tr in next_state.text_regions])
        if 'game over' in text or 'defeat' in text:
            reward -= 10.0
        elif 'victory' in text or 'ascension' in text:
            reward += 100.0
    
    return reward
```

---

### Step 4: Update CLI to Use Storage

**File to Modify**: `src/orchestrator/cli.py`

**Changes Needed**:

1. **Add cleanup command**:
```python
def cmd_cleanup(args):
    """Clean up old training data."""
    from src.orchestrator.storage_manager import StorageManager
    
    storage = StorageManager()
    
    print("🧹 Cleaning up old training data...")
    stats = storage.cleanup_old_data(dry_run=args.dry_run)
    
    print(f"\n✅ Cleanup complete:")
    print(f"  Logs archived: {stats['logs_archived']}")
    print(f"  TensorBoard runs deleted: {stats['tensorboard_runs_deleted']}")
    print(f"  Checkpoints deleted: {stats['checkpoints_deleted']}")
    
    return 0
```

2. **Add storage info command**:
```python
def cmd_storage_info(args):
    """Show storage usage information."""
    from src.orchestrator.storage_manager import StorageManager
    
    storage = StorageManager()
    info = storage.get_storage_info()
    
    print("\n📊 Storage Usage:")
    print(f"  Total: {info['total_gb']:.2f} GB")
    print(f"  Database: {info['database_bytes'] / (1024**2):.1f} MB")
    print(f"  Logs: {info['logs_bytes'] / (1024**2):.1f} MB")
    print(f"  TensorBoard: {info['tensorboard_bytes'] / (1024**2):.1f} MB")
    print(f"  Screenshots: {info['screenshots_bytes'] / (1024**2):.1f} MB")
    
    if storage.kb:
        print(f"\n📚 Database Stats:")
        print(f"  Total experiences: {storage.kb.get_total_experiences():,}")
    
    return 0
```

---

## 📋 Testing Checklist

### Test 1: Database Population
```bash
# Run a short training session
./quick_train.sh

# Check database
sqlite3 data/knowledge_base.db "
SELECT 
    (SELECT COUNT(*) FROM episodes) as episodes,
    (SELECT COUNT(*) FROM game_states) as states,
    (SELECT COUNT(*) FROM actions) as actions,
    (SELECT COUNT(*) FROM experiences) as experiences;
"

# Expected: Non-zero counts for all tables
```

### Test 2: Screenshot Saving
```bash
# Enable screenshots in config
# Edit config/storage.yaml:
#   save_screenshots: true

# Run training
./quick_train.sh

# Check screenshots
ls -lh data/sessions/screenshots/episode_*/

# Expected: PNG files for captured states
```

### Test 3: Auto Cleanup
```bash
# Run cleanup
python3 scripts/manage_data.py clean-all --execute

# Check logs archived
ls -lh data/logs/archive/

# Expected: Old logs moved and compressed
```

### Test 4: Storage Limits
```bash
# Check storage info
python3 scripts/manage_data.py info

# Expected: Shows breakdown and warns if near limit
```

---

## 🎯 Implementation Order

1. ✅ **DONE**: Full database schema
2. ✅ **DONE**: Storage configuration
3. ✅ **DONE**: StorageManager class
4. ✅ **DONE**: Data management CLI tool
5. **TODO**: Integrate StorageManager into AgentRunner
6. **TODO**: Add reward calculation
7. **TODO**: Update CLI commands
8. **TODO**: Add tests
9. **TODO**: Update documentation

---

## 🚀 Quick Start After Integration

1. **Enable database storage** (default in config)
2. **Run training**:
   ```bash
   ./start_training.sh
   ```

3. **Check database population**:
   ```bash
   sqlite3 data/knowledge_base.db "SELECT COUNT(*) FROM experiences;"
   ```

4. **View storage usage**:
   ```bash
   python3 scripts/manage_data.py info
   ```

5. **Enable screenshots** (optional):
   ```bash
   # Edit config/storage.yaml
   save_screenshots: true
   screenshot_interval: 10
   ```

6. **Auto-cleanup** (optional):
   ```bash
   # Edit config/storage.yaml
   auto_cleanup_enabled: true
   cleanup_interval_hours: 24
   ```

---

## 📊 Expected Results

After 200 episodes with full storage enabled:

**Database**:
- ~200 episodes
- ~10,000 game states
- ~30,000 actions
- ~30,000 experiences
- Database size: ~50 MB

**Storage** (without screenshots):
- Total: ~70 MB
- Logs: ~15 MB
- Database: ~50 MB
- TensorBoard: ~2 MB
- Checkpoints: ~20 KB

**Storage** (with screenshots, interval=10):
- Total: ~2 GB
- Screenshots: ~1.9 GB (2000 images)
- Database: ~50 MB
- Logs: ~15 MB

---

## ⚡ Next Steps

Run this to integrate everything:
```bash
# I'll now implement the AgentRunner integration...
```
