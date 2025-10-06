# Training Setup Guide - Collect Real Training Data

**Date**: October 5, 2025  
**Goal**: Run your first training session and collect real gameplay data

---

## ✅ Pre-Flight Checklist

### 1. Game Status
- [x] **Cultist Simulator is RUNNING** (detected at PID 37101)
- [ ] Game is on the **main gameplay screen** (not menus/settings)
- [ ] Game window is **visible and active**

### 2. System Permissions
- [ ] **Screen Recording** permission granted (System Settings → Privacy & Security → Screen Recording → Enable Terminal/Python)
- [ ] Game window is on **primary display** (for single-screen setups)

### 3. Environment Ready
```bash
# Activate virtual environment
source venv/bin/activate

# Verify installation
python3 -c "import src.vision; import src.learning; print('✓ Modules ready')"
```

---

## 🎯 Training Run Options

### Option 1: Quick Test Run (5 episodes - ~2 minutes)

**Best for**: First-time testing, verifying everything works

```bash
python3 -m src.orchestrator.cli train \
  --agent-id test_agent \
  --episodes 5 \
  --max-actions 10 \
  --checkpoint 2 \
  --verbose
```

**What this does**:
- Runs 5 short episodes (max 10 actions each)
- Saves checkpoint every 2 episodes
- Shows detailed logs
- **Duration**: ~2-3 minutes

**Expected Data Generated**:
- `data/checkpoints/checkpoint_ep2.txt`
- `data/checkpoints/checkpoint_ep4.txt`
- Session records in knowledge base
- TensorBoard metrics

---

### Option 2: Standard Training Run (50 episodes - ~20 minutes)

**Best for**: Collecting meaningful training data

```bash
python3 -m src.orchestrator.cli train \
  --agent-id my_agent \
  --episodes 50 \
  --max-actions 100 \
  --checkpoint 10 \
  --verbose
```

**What this does**:
- Runs 50 episodes (max 100 actions each)
- Saves checkpoint every 10 episodes
- Full exploration mode
- **Duration**: ~15-25 minutes

**Expected Data Generated**:
- 5 checkpoint files
- 50 session records
- TensorBoard training curves
- Action statistics

---

### Option 3: Extended Training (200 episodes - ~1-2 hours)

**Best for**: Serious training data collection

```bash
python3 -m src.orchestrator.cli train \
  --agent-id production_agent \
  --episodes 200 \
  --max-actions 150 \
  --checkpoint 20 \
  --config config/balanced.yaml
```

**What this does**:
- Runs 200 episodes
- Uses balanced configuration
- Saves every 20 episodes
- **Duration**: 1-2 hours

---

## 🚀 Step-by-Step: Your First Training Run

### Step 1: Prepare the Game

1. **Focus the Cultist Simulator window**
2. **Start or load a game** (get to the main table/gameplay view)
3. **Note the exact window title** (should be "Cultist Simulator")

### Step 2: Grant Screen Recording Permission

```bash
# Test screen capture
python3 -c "
from src.vision.screen_capture import capture_window
from src.automation.window_manager import find_window

window = find_window('Cultist Simulator')
if window:
    print(f'✓ Window found: {window}')
    img = capture_window('Cultist Simulator')
    print(f'✓ Capture works: {img.shape if img is not None else None}')
else:
    print('✗ Window not found - check window name')
"
```

**If this fails**:
1. Go to **System Settings** → **Privacy & Security** → **Screen Recording**
2. Click **+** and add **Terminal** and **Python**
3. Restart terminal
4. Try again

### Step 3: Run Your First Training Session

**Recommended: Start with Quick Test Run**

```bash
# Make sure you're in the project directory
cd /Users/stan/Documents/Programming/cultist-simulator

# Activate environment
source venv/bin/activate

# Run quick test
python3 -m src.orchestrator.cli train \
  --agent-id test_agent_001 \
  --episodes 5 \
  --max-actions 10 \
  --checkpoint 2 \
  --verbose
```

### Step 4: Monitor Training

**Watch for these indicators**:
- `✓ Window found: Cultist Simulator @ (x, y, width×height)`
- `📸 Screen captured: (width, height, 3)`
- `🔍 OCR detected: N text regions`
- `🤖 Action selected: CLICK/WAIT/KEY_PRESS`
- `✅ Action executed successfully`

**TensorBoard opens automatically**:
- Opens in VS Code or browser
- Real-time metrics visible at `http://localhost:6006`

### Step 5: Emergency Stop

**If you need to stop**:
- Press **Cmd+Shift+Q** (works even when agent controls mouse!)
- Or press **Ctrl+C** in terminal

---

## 📊 What Data Gets Collected

### During Training

**Checkpoints** (`data/checkpoints/`):
```
checkpoint_ep2.txt
checkpoint_ep4.txt
...
```
Format: Text summary of episode stats

**Session Records** (knowledge base):
```sql
SELECT * FROM sessions;  -- Episode records
SELECT * FROM experiences;  -- State-action-reward tuples
SELECT * FROM mechanics;  -- Learned patterns
```

**TensorBoard Logs** (`data/tensorboard/`):
```
events.out.tfevents.{timestamp}
```
Metrics: episodes, actions, rewards, success rate

**Training Logs** (`data/logs/`):
```
training_{timestamp}.log
```
Detailed event logs

---

## 🔍 Verifying Data Collection

### After Training Completes

```bash
# Check checkpoints
ls -lah data/checkpoints/
# Should show: checkpoint_ep*.txt files

# Check TensorBoard data
ls -lah data/tensorboard/
# Should show: events.out.tfevents.* files

# Check database records
sqlite3 data/knowledge_base.db "SELECT COUNT(*) FROM mechanics;"
# May show: 0 (mechanics learned over time)

# View logs
ls -lah data/logs/
# Should show: training log files
```

### Quick Stats Check

```bash
# Count total actions across all episodes
python3 -c "
from pathlib import Path
checkpoints = list(Path('data/checkpoints').glob('*.txt'))
print(f'Checkpoints: {len(checkpoints)}')
for cp in sorted(checkpoints)[:5]:
    print(f'  - {cp.name}')
"
```

---

## 🐛 Troubleshooting

### "Window not found"
**Solution**: 
- Verify game is running: `ps aux | grep -i cultist`
- Check exact window name: `python3 scripts/find_window.py`
- Update window name in command if different

### "Screen Recording permission denied"
**Solution**:
1. System Settings → Privacy & Security → Screen Recording
2. Enable for Terminal and Python
3. Restart terminal
4. Try again

### "No data in checkpoints/"
**Possible causes**:
- Training didn't complete (check for errors)
- Episodes too short (increase --max-actions)
- Check logs: `cat data/logs/training_*.log`

### "Agent only does WAIT actions"
**Expected**: This is normal for untrained agent!
- Agent is in test/exploration mode
- Will collect data about game state
- Needs YOLO training for better UI interaction
- After data collection, can train RL model

---

## 📈 Next Steps After Data Collection

### 1. Review Collected Data
```bash
# Count sessions
sqlite3 data/knowledge_base.db "SELECT COUNT(*) FROM sessions;"

# View TensorBoard
tensorboard --logdir data/tensorboard

# Check checkpoint summaries
cat data/checkpoints/checkpoint_ep10.txt
```

### 2. Analyze Training Results
```bash
# Show metrics
python3 -m src.orchestrator.cli metrics --agent-id test_agent_001

# View strategy
python3 -m src.orchestrator.cli strategy --agent-id test_agent_001
```

### 3. Train YOLO for UI Detection
```bash
# Label UI elements from screenshots
# Train YOLO on labeled data
# Enable YOLO in next training run
```

### 4. Train RL Model
```bash
# Use collected experiences to train RL model
# Next training run will use trained model instead of random actions
```

---

## 💡 Tips for Best Results

### Data Quality
- **Run during actual gameplay** (not menus/loading screens)
- **Let episodes complete** (don't interrupt too early)
- **Vary game states** (different scenarios, times of day, etc.)

### Performance
- **Close unnecessary apps** (free up RAM)
- **Use balanced config** for production runs
- **Monitor system resources** (Activity Monitor)

### Safety
- **Test window detection first** (scripts/find_window.py)
- **Start with short episodes** (--max-actions 10)
- **Keep emergency stop ready** (Cmd+Shift+Q)

---

## 🎯 Recommended First Session

**Copy-paste this exact command**:

```bash
# From project root
cd /Users/stan/Documents/Programming/cultist-simulator

# Activate environment
source venv/bin/activate

# Quick 5-episode test run
python3 -m src.orchestrator.cli train \
  --agent-id first_training_$(date +%Y%m%d_%H%M%S) \
  --episodes 5 \
  --max-actions 10 \
  --checkpoint 2 \
  --verbose \
  --window "Cultist Simulator"
```

**Duration**: ~2-3 minutes  
**Data Generated**: 2-3 checkpoints, 5 sessions, TensorBoard metrics  
**Safe**: Short episodes, verbose logging, easy to stop

---

## ✅ Success Criteria

After your first training run, you should see:

- [ ] Training completed without errors
- [ ] Checkpoint files in `data/checkpoints/`
- [ ] TensorBoard data in `data/tensorboard/`
- [ ] Session records can be queried
- [ ] No "permission denied" errors
- [ ] Agent detected game window correctly
- [ ] Screen captures worked
- [ ] Actions were validated and executed

**Ready to start?** Run the recommended first session command above! 🚀
