# Training Scripts - Quick Reference

## ✅ Scripts Verified and Optimized

### 1. **quick_train.sh** - Fast System Test
```bash
./quick_train.sh
```

**Configuration**:
- ⚡ Episodes: 5
- 🎯 Max Actions: 20 per episode
- 💾 Checkpoints: Every 2 episodes
- ⏱️ Duration: ~2-3 minutes
- 📊 TensorBoard: Auto-launched

**Use Cases**:
- ✓ Verify system works after code changes
- ✓ Test safety mechanisms
- ✓ Quick data collection check
- ✓ Confirm TensorBoard integration
- ✓ Validate window detection

**Expected Output**:
```
Episodes completed: 5
Total actions: ~100
Data logged: ~50 KB
TensorBoard metrics: 5 data points
```

---

### 2. **start_training.sh** - Production Training
```bash
./start_training.sh
```

**Configuration**:
- 🎯 Episodes: 200
- 🎬 Max Actions: 150 per episode
- 💾 Checkpoints: Every 20 episodes
- ⏱️ Duration: 1-2 hours
- 📊 TensorBoard: Auto-launched

**Use Cases**:
- ✓ Collect serious training data
- ✓ Prepare for RL model training
- ✓ Build YOLO training dataset
- ✓ Discover game mechanics
- ✓ Observe learning patterns

**Expected Output**:
```
Episodes completed: 200
Total actions: ~30,000
Data logged: ~15 MB
TensorBoard metrics: 200 data points
Screenshots: ~2,000 images
Checkpoints: 10 snapshots
```

---

## 🔒 Safety Features (Both Scripts)

### Emergency Stop
- **Keyboard**: `Cmd+Shift+Q` (macOS)
- **Terminal**: `Ctrl+C`
- **Effect**: Immediate shutdown, safe cleanup

### Window Bounds Verification
- Re-checks window position before EVERY action
- Prevents clicking outside game window
- Logs all boundary validations

### Action Validation
- Checks action feasibility before execution
- Prevents impossible actions
- 100% safety validation rate

---

## 📊 Monitoring Training

### TensorBoard (Auto-launched)
```
URL: http://localhost:6006
```

**Key Metrics**:
- `episode_actions`: Actions per episode (trend should stabilize)
- `episode_duration`: Time per episode (should increase as game progresses)
- `success_rate`: % of successful actions (should remain ~100%)
- `avg_action_duration`: Time per action (should be consistent)

### Live Progress (Terminal)
```
Episode 1/200 - Actions: 45, Duration: 120s
Episode 2/200 - Actions: 52, Duration: 135s
...
```

### Checkpoint Files
```bash
ls -lh data/checkpoints/
# checkpoint_ep20.txt
# checkpoint_ep40.txt
# checkpoint_ep60.txt
```

---

## 🗂️ Data Generated

### After Quick Test (5 episodes):
```
data/
├── logs/
│   └── agent_TIMESTAMP.jsonl      (~50 KB)
├── tensorboard/
│   └── test_TIMESTAMP/
│       └── events.out.tfevents.*   (~500 bytes)
├── checkpoints/
│   ├── checkpoint_ep2.txt
│   └── checkpoint_ep4.txt
└── knowledge_base.db               (~100 KB)
```

### After Production Training (200 episodes):
```
data/
├── logs/
│   └── agent_TIMESTAMP.jsonl      (~15 MB)
├── tensorboard/
│   └── production_TIMESTAMP/
│       └── events.out.tfevents.*   (~20 KB)
├── checkpoints/
│   ├── checkpoint_ep20.txt
│   ├── checkpoint_ep40.txt
│   ├── ... (10 checkpoints)
│   └── checkpoint_ep200.txt
├── sessions/
│   └── screenshots/                (~2 GB, 2000+ images)
└── knowledge_base.db               (~50 MB)
```

---

## 🎯 Decision Guide: Which Script to Run?

### Run `quick_train.sh` if:
- 🔧 You made code changes and want to verify
- ⚠️ You want to test safety features
- 🐛 You're debugging an issue
- ⏰ You only have 5 minutes
- 🧪 You want to test TensorBoard integration

### Run `start_training.sh` if:
- 🎓 You want the AI to actually learn
- 📊 You need data for RL model training
- 🖼️ You want to train YOLO on UI elements
- ⏱️ You have 1-2 hours available
- 🚀 You're ready for serious training

---

## 🔄 Typical Workflow

### Phase 1: Verification
```bash
# Test system works
./quick_train.sh

# Check TensorBoard
open http://localhost:6006

# Verify data collected
ls -lh data/logs/
ls -lh data/checkpoints/
```

### Phase 2: Production Training
```bash
# Run extended training
./start_training.sh

# Monitor progress
# (TensorBoard auto-opens)

# Wait for completion (1-2 hours)
```

### Phase 3: Analysis
```bash
# Review TensorBoard metrics
# Look for:
#   - Consistent action counts
#   - Stable durations
#   - No crashes or errors

# Check logs
tail -100 data/logs/agent_*.jsonl | jq

# Analyze checkpoints
cat data/checkpoints/checkpoint_ep200.txt
```

### Phase 4: Next Training Stage (Future)
```bash
# Train YOLO on collected screenshots
python -m src.vision.train_yolo --data data/sessions/

# Train RL model on collected experiences
python -m src.learning.train_rl --episodes 200
```

---

## ⚙️ Script Internals

### Both Scripts Do:
1. ✓ Change to project directory
2. ✓ Activate virtual environment
3. ✓ Kill old TensorBoard processes
4. ✓ Start fresh TensorBoard instance
5. ✓ Run training with optimal parameters
6. ✓ Display results and next steps

### Command Executed:
```bash
python3 -m src.orchestrator.cli train \
  --agent-id "UNIQUE_ID_TIMESTAMP" \
  --episodes NUMBER \
  --max-actions LIMIT \
  --checkpoint INTERVAL \
  --window "Cultist Simulator" \
  --verbose
```

### Parameters Explained:
- `--agent-id`: Unique identifier for this training run
- `--episodes`: Number of game sessions to run
- `--max-actions`: Safety limit per episode (prevents infinite loops)
- `--checkpoint`: Save progress every N episodes
- `--window`: Game window title to detect
- `--verbose`: Enable DEBUG-level logging

---

## 🐛 Troubleshooting

### TensorBoard Shows "No Data"
```bash
# Check event files exist
find data/tensorboard -name "*.tfevents*"

# If empty, verify logger instantiated
grep "TensorBoard" data/logs/agent_*.jsonl

# Restart TensorBoard
pkill -f tensorboard
tensorboard --logdir data/tensorboard
```

### Window Not Detected
```bash
# List all windows
python scripts/find_window.py

# Verify game running
ps aux | grep "Cultist Simulator"

# Check game window title exactly matches
```

### Agent Clicking Outside Window
```bash
# This should be FIXED now
# Verify fix in logs:
grep "Window bounds re-verified" data/logs/agent_*.jsonl

# Should see bounds check before EVERY action
```

### Training Hangs
```bash
# Use emergency stop: Cmd+Shift+Q
# Or terminal: Ctrl+C

# Check last log entry
tail -20 data/logs/agent_*.jsonl

# Resume from checkpoint
# (currently manual - automatic resume TODO)
```

---

## 📈 Success Criteria

### Quick Test Success:
- ✅ 5 episodes complete without crash
- ✅ TensorBoard shows 5 data points
- ✅ All actions pass safety validation
- ✅ Log file created with ~1000 events
- ✅ Checkpoint files exist

### Production Training Success:
- ✅ 200 episodes complete
- ✅ TensorBoard shows learning curves
- ✅ ~30,000 actions logged
- ✅ Zero safety violations
- ✅ 10 checkpoint snapshots created
- ✅ Database has rich state/action history

---

## 🚀 Ready to Train!

**Quick verification**: `./quick_train.sh` (3 minutes)

**Full training**: `./start_training.sh` (1-2 hours)

**Monitor**: http://localhost:6006

**Stop anytime**: `Cmd+Shift+Q` or `Ctrl+C`

**Read more**: See `HOW_LEARNING_WORKS.md` for details on the learning process!
