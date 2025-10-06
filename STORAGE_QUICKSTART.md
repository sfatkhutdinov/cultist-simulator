# 🚀 Storage System Quick Start

## One-Line Summary
**Your agent now automatically stores all training data to a 6-table SQLite database with configurable retention policies.**

---

## ⚡ Quick Commands

### View Storage Status
```bash
python scripts/manage_data.py info
```

### Clean Up Old Data
```bash
# Archive logs older than 30 days
python scripts/manage_data.py clean-logs --days 30

# Keep only last 10 TensorBoard runs
python scripts/manage_data.py clean-tensorboard --keep 10

# Compact database (frees space)
python scripts/manage_data.py compact

# Do all cleanup operations
python scripts/manage_data.py clean-all
```

### Query Database Directly
```bash
# Show all episodes
sqlite3 data/knowledge_base.db "SELECT * FROM episodes;"

# Count total experiences
sqlite3 data/knowledge_base.db "SELECT COUNT(*) FROM experiences;"

# Show recent actions
sqlite3 data/knowledge_base.db "SELECT * FROM actions ORDER BY timestamp DESC LIMIT 10;"

# Episode statistics
sqlite3 data/knowledge_base.db "
  SELECT 
    e.id,
    e.outcome,
    e.total_actions,
    COUNT(DISTINCT gs.id) as states_captured,
    COUNT(DISTINCT ex.id) as experiences_stored
  FROM episodes e
  LEFT JOIN game_states gs ON e.id = gs.episode_id
  LEFT JOIN experiences ex ON e.id = ex.episode_id
  GROUP BY e.id;
"
```

---

## 📊 What Gets Stored

### Automatically (No Config Needed)
- ✅ **Episodes**: Start/end time, outcome, duration, action count
- ✅ **Actions**: Type, parameters, success status, execution time
- ✅ **Game States**: OCR text, detected elements, window bounds
- ✅ **Experiences**: State-Action-Reward-State (SARS) tuples for RL
- ✅ **Mechanics**: Learned game rules (future use)
- ✅ **Patterns**: Discovered action sequences (future use)

### Optional (Enable in Config)
- 📸 **Screenshots**: Visual captures every N actions
  - Edit `config/storage.yaml` → `save_screenshots: true`
  - Set interval: `screenshot_interval: 5`  # every 5 actions

---

## 🎛️ Configuration

Edit `config/storage.yaml` to customize:

```yaml
storage:
  # Database
  enable_database_storage: true        # Set false to disable all DB writes
  
  # Screenshots (disabled by default to save space)
  save_screenshots: false              # Enable visual capture
  screenshot_interval: 5               # Save every 5 actions
  screenshot_format: png               # png or jpeg
  screenshot_quality: 85               # 1-100 for jpeg
  
  # Logs
  log_retention_days: 30               # Archive logs older than this
  compress_archived_logs: true         # Gzip old logs
  
  # TensorBoard
  tensorboard_keep_runs: 10            # Keep last N runs
  
  # Auto-cleanup (disabled by default - run manually)
  auto_cleanup_enabled: false          # Enable automatic cleanup
  cleanup_interval_hours: 24           # How often to clean
  
  # Storage limits
  max_total_storage_gb: 10             # Hard limit
  warn_storage_gb: 5                   # Warning threshold
```

---

## 🔍 Monitoring Storage

### Check Size Before Training
```bash
python scripts/manage_data.py info
```

### During Training
The agent will display storage stats after each episode:
```
📊 Episode Complete
   States captured: 42
   Experiences stored: 41
   Database size: 2.3 MB
```

### After Training
```bash
# See what was captured
sqlite3 data/knowledge_base.db "
  SELECT 
    COUNT(*) as total_episodes,
    SUM(total_actions) as total_actions,
    SUM(duration_seconds)/3600.0 as total_hours
  FROM episodes;
"
```

---

## 🧹 Cleanup Workflow

### Daily Cleanup (Recommended)
```bash
# Quick cleanup - safe to run anytime
python scripts/manage_data.py clean-logs --days 30
python scripts/manage_data.py clean-tensorboard --keep 10
```

### Weekly Cleanup (Recommended)
```bash
# Full cleanup + database optimization
python scripts/manage_data.py clean-all
python scripts/manage_data.py compact
```

### Emergency Cleanup (Out of Space)
```bash
# Aggressive cleanup
python scripts/manage_data.py clean-logs --days 7   # Keep only 1 week
python scripts/manage_data.py clean-tensorboard --keep 3  # Keep only 3 runs
python scripts/manage_data.py compact

# If still out of space, manually delete old episodes
sqlite3 data/knowledge_base.db "
  DELETE FROM episodes 
  WHERE start_time < datetime('now', '-30 days');
"
python scripts/manage_data.py compact
```

---

## 📈 Analyzing Training Data

### Episode Success Rate
```bash
sqlite3 data/knowledge_base.db "
  SELECT 
    outcome,
    COUNT(*) as count,
    AVG(duration_seconds) as avg_duration,
    AVG(total_actions) as avg_actions
  FROM episodes
  GROUP BY outcome;
"
```

### Most Common Actions
```bash
sqlite3 data/knowledge_base.db "
  SELECT 
    action_type,
    COUNT(*) as count,
    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
  FROM actions
  GROUP BY action_type
  ORDER BY count DESC
  LIMIT 10;
"
```

### Reward Distribution
```bash
sqlite3 data/knowledge_base.db "
  SELECT 
    CAST(reward AS INT) as reward_bucket,
    COUNT(*) as count
  FROM experiences
  GROUP BY CAST(reward AS INT)
  ORDER BY reward_bucket;
"
```

### Learning Progress Over Time
```bash
sqlite3 data/knowledge_base.db "
  SELECT 
    DATE(e.start_time) as day,
    COUNT(DISTINCT e.id) as episodes,
    AVG(e.duration_seconds) as avg_duration,
    SUM(CASE WHEN e.outcome = 'victory' THEN 1 ELSE 0 END) as victories
  FROM episodes e
  GROUP BY DATE(e.start_time)
  ORDER BY day;
"
```

---

## 🎓 Advanced Usage

### Export Training Data
```python
# Python script to export episode data
import sqlite3
import json

conn = sqlite3.connect('data/knowledge_base.db')
cursor = conn.cursor()

# Get episode with all related data
cursor.execute("""
    SELECT 
        e.*,
        (SELECT json_group_array(json_object(
            'id', gs.id,
            'timestamp', gs.timestamp,
            'ocr_text', gs.ocr_text
        )) FROM game_states gs WHERE gs.episode_id = e.id) as states,
        (SELECT json_group_array(json_object(
            'id', a.id,
            'action_type', a.action_type,
            'success', a.success
        )) FROM actions a WHERE a.episode_id = e.id) as actions
    FROM episodes e
    WHERE e.id = 1
""")

episode = cursor.fetchone()
print(json.dumps(dict(episode), indent=2))
```

### Replay Episode from Database
```python
# Load and replay an episode
from src.learning.knowledge_base import KnowledgeBase

kb = KnowledgeBase()
stats = kb.get_episode_stats(episode_id=1)

print(f"Episode {stats['episode_id']}")
print(f"Outcome: {stats['outcome']}")
print(f"Duration: {stats['duration_seconds']}s")
print(f"Actions: {stats['total_actions']}")
print(f"States: {stats['states_captured']}")
print(f"Experiences: {stats['experiences_stored']}")
```

---

## ⚠️ Troubleshooting

### "Database locked" error
```bash
# Check for zombie connections
lsof data/knowledge_base.db

# Force close all connections
pkill -f "python.*cultist"

# Compact to fix corruption
python scripts/manage_data.py compact
```

### Storage filling up too fast
```bash
# Check what's using space
python scripts/manage_data.py info

# If screenshots are the issue:
# 1. Disable in config: save_screenshots: false
# 2. Delete existing screenshots:
find data/sessions -name "*.png" -delete

# If database is too large:
# Delete old episodes (keeps last 100)
sqlite3 data/knowledge_base.db "
  DELETE FROM episodes 
  WHERE id NOT IN (
    SELECT id FROM episodes 
    ORDER BY start_time DESC 
    LIMIT 100
  );
"
python scripts/manage_data.py compact
```

### Database corruption
```bash
# Check integrity
sqlite3 data/knowledge_base.db "PRAGMA integrity_check;"

# If corrupted, export and recreate
sqlite3 data/knowledge_base.db ".dump" > backup.sql
mv data/knowledge_base.db data/knowledge_base.db.corrupt
sqlite3 data/knowledge_base.db < backup.sql
```

---

## 🎯 Best Practices

1. **Regular Cleanup**: Run `clean-all` weekly
2. **Monitor Size**: Check storage before long training runs
3. **Enable Compression**: Keep `compress_archived_logs: true`
4. **Limit Screenshots**: Only enable when debugging vision issues
5. **Archive Important Runs**: Copy successful episode data before cleanup
6. **Backup Database**: Before major experiments, copy `knowledge_base.db`

---

## 📝 Notes

- **Thread-Safe**: All storage operations are safe for concurrent use
- **Graceful Degradation**: If storage fails, training continues (just logs warning)
- **Zero Configuration**: Works out of the box with sensible defaults
- **SQL Access**: Full access to raw data via sqlite3 CLI or Python

---

*Generated: 2025-10-06 00:22*
*Storage system operational and ready for use* ✅
