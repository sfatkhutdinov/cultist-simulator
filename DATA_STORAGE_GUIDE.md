# Data Storage & Management - Complete Guide

## 📊 Current State Analysis

### Storage Summary:
```
data/
├── logs/           → 1.1 MB, 8,129 log entries across 5 files
├── checkpoints/    → 4 snapshot files
├── tensorboard/    → 3 event file directories
├── sessions/       → Empty (screenshots not saved yet)
└── knowledge_base.db → 12 KB, 1 table (mechanics), 0 rows
```

---

## 🗂️ Where Everything is Stored

### 1. **Training Logs** (`data/logs/`)
**Location**: `data/logs/agent_YYYYMMDD_HHMMSS.jsonl`

**What's Stored**:
- Every event during training (JSON lines format)
- Vision captures (OCR results, detected elements)
- Action selections and executions
- Safety validations
- Episode completions
- Errors and warnings

**Example Entry**:
```json
{
  "event": "vision_capture",
  "timestamp": "2025-10-06T03:56:40.123456Z",
  "ocr_text": ["Health", "Work", "Funds"],
  "color_regions": [{"color": "blue", "bounds": [100, 200, 50, 30]}],
  "logger": "src.vision"
}
```

**Current Size**: 
- Latest file: 488 KB (3,517 lines)
- Total: ~1.1 MB across 5 files

**Rotation**: ❌ **NOT IMPLEMENTED**
- Files accumulate indefinitely
- Each training run creates a new file (timestamped)
- Old files never deleted automatically

---

### 2. **Checkpoints** (`data/checkpoints/`)
**Location**: `data/checkpoints/checkpoint_ep{N}.txt`

**What's Stored**:
- Episode summary snapshots
- Created every N episodes (configurable)
- Plain text format for easy reading

**Example**:
```
Episode: 2
Total Actions: 60
Avg Duration: 135.5s
Success Rate: 100.0%
Timestamp: 2025-10-06T03:52:40
```

**Current Size**: 4 files (small, ~200 bytes each)

**Rotation**: ❌ **NOT IMPLEMENTED**
- Checkpoints accumulate with each training run
- Episode numbers may overlap between runs
- No cleanup mechanism

---

### 3. **TensorBoard Metrics** (`data/tensorboard/`)
**Location**: `data/tensorboard/{agent_id}_{timestamp}/events.out.tfevents.*`

**What's Stored**:
- Numerical training metrics
- Episode statistics (actions, duration, success rate)
- Scalar values for graphing
- Binary protocol buffer format

**Metrics Tracked**:
```python
episode/actions          # Actions taken per episode
episode/duration         # Episode length in seconds
episode/success_rate     # % of successful actions
episode/total_actions    # Cumulative actions
episode/avg_action_duration  # Time per action
episode/loop_detections  # Number of loops detected
episode/safety_violations    # Safety check failures
```

**Current Size**: 3 directories, ~20 KB total

**Rotation**: ❌ **NOT IMPLEMENTED**
- Each training run creates a new timestamped directory
- Old metrics never deleted
- Can accumulate GBs over time

---

### 4. **Knowledge Base** (`data/knowledge_base.db`)
**Location**: `data/knowledge_base.db` (SQLite)

**Schema**:
```sql
CREATE TABLE mechanics (
    name TEXT PRIMARY KEY,
    description TEXT,
    conditions TEXT,      -- JSON
    effects TEXT,         -- JSON (full data)
    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**What SHOULD Be Stored**:
- Learned game mechanics
- Discovered patterns
- Card combinations
- Successful strategies

**What's ACTUALLY Stored**: 
- ❌ **NOTHING** (0 rows in mechanics table)
- ❌ **No other tables** (only 1 table exists)

**Why Only 1 Table?**
The database was designed with only `mechanics` table for Phase 1. Other tables were planned but not implemented:

**Missing Tables** (TODO):
```sql
-- NOT IMPLEMENTED:
CREATE TABLE sessions (...);      -- Episode metadata
CREATE TABLE states (...);        -- Game states
CREATE TABLE actions (...);       -- Actions taken
CREATE TABLE rewards (...);       -- Rewards received
CREATE TABLE patterns (...);      -- Discovered patterns
CREATE TABLE strategies (...);    -- Successful sequences
```

**Why Nothing is Stored?**
Looking at the code:
```python
# src/learning/knowledge_base.py
def store_experience(self, state, action, next_state, reward):
    """Store a single experience tuple (SARS)."""
    # Placeholder implementation
    # TODO T096: Implement actual storage
    logger.debug("experience_stored", reward=reward)  # ← Just logs, doesn't store!
```

**Result**: Training runs collect data in logs but DON'T populate the database!

---

### 5. **Sessions/Screenshots** (`data/sessions/`)
**Location**: `data/sessions/screenshots/`

**What SHOULD Be Stored**:
- Game screenshots for YOLO training
- Visual training data
- ~2,000+ images after 200 episodes

**What's ACTUALLY Stored**: 
- ❌ **NOTHING** (directory empty)

**Why?**
Screenshot saving is not enabled by default:
```python
# Screenshots are captured but not saved to disk
# Only stored in memory during episode
# Would need explicit save flag to persist
```

---

## 🔄 Data Lifecycle (Current Behavior)

### During Training:
```
1. Episode starts
   ↓
2. Agent captures screen → Stored in MEMORY
   ↓
3. OCR extracts text → Logged to JSONL file
   ↓
4. Agent selects action → Logged to JSONL file
   ↓
5. Action executed → Logged to JSONL file
   ↓
6. Safety checks → Logged to JSONL file
   ↓
7. Episode ends
   ↓
8. Metrics → Sent to TensorBoard
   ↓
9. Checkpoint → Saved to checkpoints/ (every N episodes)
   ↓
10. Screenshot → DISCARDED (not saved)
    ↓
11. Experience → NOT stored in database
```

### After Training:
- **Logs**: Remain on disk forever (no cleanup)
- **TensorBoard**: Remains on disk forever (no cleanup)
- **Checkpoints**: Remain on disk forever (no cleanup)
- **Database**: Remains empty (no data inserted)
- **Screenshots**: Lost (never saved)

---

## ⚠️ Current Issues

### 1. **No Database Population**
**Problem**: Knowledge base is empty despite training  
**Impact**: Can't learn from past experiences  
**Why**: `store_experience()` is a stub (TODO T096)

### 2. **No Data Cleanup**
**Problem**: Files accumulate indefinitely  
**Impact**: Disk usage grows unbounded  
**Why**: No rotation/archival mechanism implemented

### 3. **No Screenshot Persistence**
**Problem**: Visual data discarded  
**Impact**: Can't train YOLO model  
**Why**: Screenshot saving not enabled

### 4. **Limited Database Schema**
**Problem**: Only 1 table exists  
**Impact**: Can't track sessions, states, actions properly  
**Why**: Minimal schema for Phase 1, expansion not implemented

### 5. **No Log Rotation**
**Problem**: Each training run creates new log file  
**Impact**: Directory clutters with timestamped files  
**Why**: No log management system

---

## 🛠️ What SHOULD Happen

### Ideal Data Flow:

#### **Phase 1: Collection** (Current - Mostly Working)
```
Training → Logs (JSONL) → ✅ Working
Training → TensorBoard → ✅ Working
Training → Checkpoints → ✅ Working
Training → Screenshots → ❌ NOT IMPLEMENTED
Training → Database → ❌ NOT IMPLEMENTED
```

#### **Phase 2: Storage** (Planned - Not Implemented)
```
Logs → Parsed → Database (sessions, states, actions)
Screenshots → Organized → data/sessions/screenshots/{episode}/
Old Logs → Archived → data/logs/archive/
Old TensorBoard → Cleaned → Keep last 10 runs
```

#### **Phase 3: Learning** (Future)
```
Database → Training Data → RL Model
Screenshots → Annotations → YOLO Model
Mechanics → Pattern Recognition → Strategy
```

---

## 📝 Recommended Improvements

### Priority 1: Database Population (Critical)

**Implement Missing Tables**:
```sql
CREATE TABLE episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_actions INTEGER,
    duration_seconds REAL,
    outcome TEXT,  -- 'victory', 'defeat', 'timeout'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE game_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id INTEGER,
    timestamp TIMESTAMP,
    screenshot_path TEXT,
    ocr_text TEXT,  -- JSON array
    detected_elements TEXT,  -- JSON array
    window_bounds TEXT,  -- JSON object
    FOREIGN KEY (episode_id) REFERENCES episodes(id)
);

CREATE TABLE actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id INTEGER,
    state_id INTEGER,
    action_type TEXT,  -- CLICK, DRAG, KEY_PRESS
    parameters TEXT,  -- JSON
    success BOOLEAN,
    timestamp TIMESTAMP,
    FOREIGN KEY (episode_id) REFERENCES episodes(id),
    FOREIGN KEY (state_id) REFERENCES game_states(id)
);

CREATE TABLE experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_id INTEGER,
    action_id INTEGER,
    next_state_id INTEGER,
    reward REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES game_states(id),
    FOREIGN KEY (action_id) REFERENCES actions(id),
    FOREIGN KEY (next_state_id) REFERENCES game_states(id)
);
```

**Implement store_experience()**:
```python
def store_experience(self, state, action, next_state, reward):
    """Actually store to database, not just log."""
    cursor = self.conn.cursor()
    
    # Insert state
    state_id = self._insert_state(state)
    
    # Insert action
    action_id = self._insert_action(action, state_id)
    
    # Insert next state
    next_state_id = self._insert_state(next_state)
    
    # Insert experience
    cursor.execute("""
        INSERT INTO experiences (state_id, action_id, next_state_id, reward)
        VALUES (?, ?, ?, ?)
    """, (state_id, action_id, next_state_id, reward))
    
    self.conn.commit()
```

### Priority 2: Screenshot Persistence

**Add to agent_runner.py**:
```python
def _save_screenshot(self, episode_num: int, action_num: int, image_data):
    """Save screenshot for YOLO training."""
    episode_dir = Path(f"data/sessions/screenshots/episode_{episode_num:04d}")
    episode_dir.mkdir(parents=True, exist_ok=True)
    
    screenshot_path = episode_dir / f"action_{action_num:04d}.png"
    # Save image_data to screenshot_path
```

### Priority 3: Data Cleanup/Rotation

**Add data management script** (`scripts/manage_data.py`):
```python
def cleanup_old_logs(keep_days=30):
    """Archive logs older than N days."""
    archive_dir = Path("data/logs/archive")
    archive_dir.mkdir(exist_ok=True)
    
    for log_file in Path("data/logs").glob("agent_*.jsonl"):
        if is_older_than(log_file, keep_days):
            shutil.move(log_file, archive_dir / log_file.name)
            gzip_file(archive_dir / log_file.name)  # Compress

def cleanup_tensorboard(keep_runs=10):
    """Keep only the N most recent TensorBoard runs."""
    runs = sorted(Path("data/tensorboard").iterdir(), 
                  key=lambda p: p.stat().st_mtime)
    
    for old_run in runs[:-keep_runs]:
        shutil.rmtree(old_run)

def compact_database():
    """Run VACUUM on SQLite database to reclaim space."""
    conn = sqlite3.connect("data/knowledge_base.db")
    conn.execute("VACUUM")
    conn.close()
```

### Priority 4: Add Storage Configuration

**Add to config files**:
```yaml
storage:
  save_screenshots: true
  screenshot_interval: 1  # Save every N actions
  max_log_size_mb: 100
  log_retention_days: 30
  tensorboard_keep_runs: 10
  checkpoint_interval: 20
  enable_database_storage: true
```

---

## 🎯 Quick Fixes You Can Apply Now

### 1. Manual Log Cleanup
```bash
# Move old logs to archive
mkdir -p data/logs/archive
find data/logs -name "agent_*.jsonl" -mtime +7 -exec mv {} data/logs/archive/ \;

# Compress archived logs
gzip data/logs/archive/*.jsonl
```

### 2. TensorBoard Cleanup
```bash
# Keep only last 5 runs
cd data/tensorboard
ls -t | tail -n +6 | xargs rm -rf
```

### 3. Check Disk Usage
```bash
# See what's using space
du -sh data/*
du -sh data/logs/* | sort -h
```

### 4. Manual Database Inspection
```bash
# Check database size
ls -lh data/knowledge_base.db

# View schema
sqlite3 data/knowledge_base.db ".schema"

# Count rows
sqlite3 data/knowledge_base.db "SELECT COUNT(*) FROM mechanics;"
```

---

## 📊 Storage Estimates

### After 200 Episodes (Projected):
```
Logs:           ~15 MB  (uncompressed JSONL)
TensorBoard:    ~2 MB   (metrics)
Checkpoints:    ~20 KB  (10 snapshots)
Screenshots:    ~2 GB   (if enabled, 2000+ PNG images)
Database:       ~50 MB  (if fully implemented)
───────────────────────
Total:          ~2 GB   (with screenshots)
                ~70 MB  (current, without screenshots/DB)
```

### After 1000 Episodes:
```
Logs:           ~75 MB
TensorBoard:    ~10 MB
Checkpoints:    ~100 KB
Screenshots:    ~10 GB
Database:       ~250 MB
───────────────────────
Total:          ~10 GB
```

---

## ✅ Action Plan

### Immediate (Today):
1. Document current storage behavior ✅ (this document)
2. Manually clean old logs/TensorBoard
3. Decide if screenshots are needed

### Short-term (This Week):
1. Implement full database schema
2. Implement `store_experience()` properly
3. Add screenshot saving (optional flag)
4. Create data cleanup script

### Medium-term (This Month):
1. Add log rotation mechanism
2. Add TensorBoard run management
3. Add storage configuration options
4. Create data analysis/export tools

### Long-term (Future):
1. Add data export to training formats (CSV, NumPy arrays)
2. Add data visualization tools
3. Implement database indexing for performance
4. Add data compression for old episodes

---

## 🔍 Summary

**Where Data Goes**:
- ✅ Logs → `data/logs/*.jsonl` (kept forever)
- ✅ Metrics → `data/tensorboard/*/events.*` (kept forever)
- ✅ Checkpoints → `data/checkpoints/*.txt` (kept forever)
- ❌ Screenshots → Nowhere (discarded)
- ❌ Experiences → Nowhere (not stored in DB)

**Why Database is Empty**:
- Only `mechanics` table exists
- No other tables implemented
- `store_experience()` is a stub (doesn't actually store)
- Database designed for future use, not currently active

**What Needs Fixing**:
1. Implement full database schema
2. Implement actual storage in `store_experience()`
3. Add data cleanup/rotation
4. Add screenshot persistence (optional)
5. Add storage configuration

**Current Storage**: ~70 MB per 200 episodes  
**Projected Storage**: ~2 GB per 200 episodes (with all features)
