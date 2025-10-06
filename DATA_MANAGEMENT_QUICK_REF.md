# Quick Answers: Data Storage & Management

## Where Does Training Output Go?

### 📝 Logs (Main Output) → `data/logs/`
**Current**: 1.1 MB across 5 files

Every training run creates: `agent_YYYYMMDD_HHMMSS.jsonl`

**Contains**:
- Every vision capture (OCR results, colors detected)
- Every action selected and executed
- Every safety validation
- Episode completions
- All errors/warnings

**Format**: JSON Lines (one JSON object per line)

**Example**:
```bash
tail -5 data/logs/agent_20251005_235656.jsonl
```

---

### 📊 TensorBoard (Metrics) → `data/tensorboard/`
**Current**: 2.7 KB across 3 runs

Each training run creates: `{agent_id}_{timestamp}/events.out.tfevents.*`

**Contains**:
- Episode statistics (actions, duration, success rate)
- Graphs over time
- Binary format (view with TensorBoard)

**View**:
```bash
tensorboard --logdir data/tensorboard
open http://localhost:6006
```

---

### 💾 Checkpoints (Snapshots) → `data/checkpoints/`
**Current**: 696 bytes across 3 files

Created every N episodes: `checkpoint_ep{N}.txt`

**Contains**:
- Episode number
- Total actions
- Average duration
- Success rate
- Timestamp

**Example**:
```bash
cat data/checkpoints/checkpoint_ep2.txt
```

---

### 🗄️ Database (Knowledge) → `data/knowledge_base.db`
**Current**: 12 KB, **EMPTY** (0 rows)

SQLite database with 1 table: `mechanics`

**Why Empty?**
- `store_experience()` function is a stub (TODO T096)
- Just logs to files, doesn't insert into database
- Designed for future use, not actively used yet

**Inspect**:
```bash
sqlite3 data/knowledge_base.db ".schema"
sqlite3 data/knowledge_base.db "SELECT * FROM mechanics;"
```

---

### 📸 Screenshots → `data/sessions/screenshots/`
**Current**: Empty directory

**Why Empty?**
- Screenshots captured in memory but NOT saved to disk
- Would need explicit save flag to persist
- Needed for YOLO training (future)

---

## Why Only 1 Table in Database?

### Current Schema:
```sql
CREATE TABLE mechanics (
    name TEXT PRIMARY KEY,
    description TEXT,
    conditions TEXT,
    effects TEXT,
    learned_at TIMESTAMP
);
```

### Why So Minimal?

1. **Phase 1 Design**: Database was set up for future expansion
2. **Not Actively Used**: Training data goes to logs, not database
3. **Stub Implementation**: Code exists but doesn't populate database

### What's Missing (TODO):
```sql
-- These tables don't exist yet:
episodes      -- Episode metadata
game_states   -- Screen captures, OCR results
actions       -- Actions taken
experiences   -- State-action-reward tuples
patterns      -- Discovered patterns
strategies    -- Successful sequences
```

### Where Data Actually Goes:
```
Vision capture → Logged to JSONL file ❌ Not in database
Action taken   → Logged to JSONL file ❌ Not in database
Episode done   → Logged to JSONL file ❌ Not in database
                 Metrics to TensorBoard
                 Snapshot to checkpoint
```

---

## How is Data Maintained?

### Current Behavior: **NO CLEANUP** ❌

**What Happens**:
- ✅ Files created during training
- ❌ Files never cleaned
- ❌ Files never archived
- ❌ Files never compressed
- ❌ No size limits
- ❌ No rotation

**Result**: Files accumulate indefinitely

### Storage Growth:
```
After 5 training runs:   ~1 MB (current)
After 20 training runs:  ~5 MB
After 100 training runs: ~25 MB
After 1000 episodes:     ~100 MB - 10 GB (with screenshots)
```

---

## Data Management Tool (NEW!)

I created `scripts/manage_data.py` to help manage storage:

### View Storage Info:
```bash
python3 scripts/manage_data.py info
```
Shows:
- Total storage used
- Breakdown by type
- Recent files
- Database info

### Clean Old Logs (Dry Run):
```bash
python3 scripts/manage_data.py clean-logs --days 7
```
Preview what would be archived

### Clean Old Logs (Execute):
```bash
python3 scripts/manage_data.py clean-logs --days 7 --execute
```
Actually archives and compresses logs older than 7 days

### Clean TensorBoard Runs:
```bash
# Keep only 5 most recent runs
python3 scripts/manage_data.py clean-tensorboard --keep 5 --execute
```

### Compact Database:
```bash
python3 scripts/manage_data.py compact --execute
```
Reclaims unused space in SQLite

### Clean Everything:
```bash
python3 scripts/manage_data.py clean-all --execute
```
Runs all cleanup tasks

---

## Recommended Workflow

### Weekly Maintenance:
```bash
# Check storage
python3 scripts/manage_data.py info

# Clean old data (if needed)
python3 scripts/manage_data.py clean-logs --days 14 --execute
python3 scripts/manage_data.py clean-tensorboard --keep 10 --execute
```

### Monthly Maintenance:
```bash
# Full cleanup
python3 scripts/manage_data.py clean-all --execute

# Archive important runs manually
mkdir -p data/archive/important_runs
cp -r data/tensorboard/production_* data/archive/important_runs/
```

### Before Long Training:
```bash
# Check available space
df -h .
du -sh data/

# Clean if needed
python3 scripts/manage_data.py clean-all --execute
```

---

## What Needs Fixing (Priority Order)

### 🔴 Priority 1: Database Population
**Problem**: Database empty, no learning from history  
**Fix**: Implement full schema + `store_experience()`  
**Impact**: Enable actual learning from past episodes

### 🟡 Priority 2: Data Cleanup
**Problem**: Files accumulate forever  
**Fix**: Add automatic log rotation/archival  
**Impact**: Prevent disk from filling up

### 🟡 Priority 3: Screenshot Persistence
**Problem**: Visual data discarded  
**Fix**: Add optional screenshot saving  
**Impact**: Enable YOLO training

### 🟢 Priority 4: Storage Configuration
**Problem**: No control over what/how much to save  
**Fix**: Add config options for storage behavior  
**Impact**: Customize storage per use case

---

## Quick Commands Reference

### Check What You Have:
```bash
# Storage overview
python3 scripts/manage_data.py info

# List log files
ls -lh data/logs/

# List TensorBoard runs
ls -lh data/tensorboard/

# Check database
sqlite3 data/knowledge_base.db "SELECT name FROM sqlite_master WHERE type='table';"
```

### Clean Up Space:
```bash
# Preview cleanup (safe)
python3 scripts/manage_data.py clean-logs --days 7

# Actually clean (removes files!)
python3 scripts/manage_data.py clean-logs --days 7 --execute
```

### Analyze Logs:
```bash
# Count events in latest log
wc -l data/logs/agent_*.jsonl | tail -1

# See event types
grep -o '"event":"[^"]*"' data/logs/agent_20251005_235656.jsonl | sort | uniq -c

# Extract errors
grep '"level":"error"' data/logs/agent_*.jsonl
```

---

## Summary

✅ **Data is being collected** (logs, metrics, checkpoints)  
❌ **Database is NOT being used** (empty, stub implementation)  
❌ **No automatic cleanup** (files accumulate forever)  
❌ **Screenshots NOT saved** (discarded after each episode)  

**Use the new `manage_data.py` tool to view and clean storage!**

For full details, see: `DATA_STORAGE_GUIDE.md`
