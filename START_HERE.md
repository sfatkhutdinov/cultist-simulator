# Ready to Collect Training Data! 🚀

**Status**: ✅ All systems ready  
**Game**: Cultist Simulator is running (PID 37101)  
**Window**: Detected at (48, 54) - 881×630 pixels  
**Permissions**: Screen capture working  
**Date**: October 5, 2025

---

## Quick Start - Collect Your First Training Data

### Option 1: Use the Quick Training Script (Recommended)

```bash
./quick_train.sh
```

This will:
- Run 5 short episodes (10 actions each)
- Save 2-3 checkpoints
- Collect session data
- Generate TensorBoard metrics
- **Duration**: ~2-3 minutes

### Option 2: Manual Command

```bash
# Activate environment first
source venv/bin/activate

# Run training
python3 -m src.orchestrator.cli train \
  --agent-id test_agent_001 \
  --episodes 5 \
  --max-actions 10 \
  --checkpoint 2 \
  --window "Cultist Simulator" \
  --verbose
```

### Option 3: Extended Training Session

```bash
source venv/bin/activate

python3 -m src.orchestrator.cli train \
  --agent-id extended_$(date +%Y%m%d) \
  --episodes 50 \
  --max-actions 100 \
  --checkpoint 10 \
  --window "Cultist Simulator" \
  --verbose
```

**Duration**: ~15-25 minutes

---

## What You'll See During Training

```
🤖 CULTIST SIMULATOR AI AGENT - RUNNING
======================================================================
  Session ID: abc123
  Agent ID: test_agent_001
  Max Actions: 10
  Mode: Test (Random Exploration)

  🛑 EMERGENCY STOP:
     Press Cmd+Shift+Q to stop from anywhere
     Or press Ctrl+C in terminal
======================================================================

[Episode 1/5]
  ✓ Window active: Cultist Simulator @ (48, 54)
  📸 Screen captured: (630, 881, 3)
  🔍 OCR: 12 text regions detected
  🎯 YOLO: 0 elements (untrained)
  🤖 Action: WAIT (1000ms)
  ✅ Executed successfully
  ...

[Checkpoint] Saved to data/checkpoints/checkpoint_ep2.txt

[Episode 2/5]
  ...

✅ Training Complete!
Episodes: 5
Total Actions: 45
Average Episode Length: 9.0 actions
```

---

## Verify Data Collection

After training completes, check what data was collected:

```bash
# 1. Check checkpoints
ls -lah data/checkpoints/
# Should show: checkpoint_ep2.txt, checkpoint_ep4.txt, etc.

# 2. Check TensorBoard data
ls -lah data/tensorboard/
# Should show: events.out.tfevents.* files

# 3. View a checkpoint summary
cat data/checkpoints/checkpoint_ep2.txt

# 4. Query database (if session storage is implemented)
sqlite3 data/knowledge_base.db "SELECT COUNT(*) FROM mechanics;"

# 5. Launch TensorBoard to visualize metrics
tensorboard --logdir data/tensorboard
# Open: http://localhost:6006
```

---

## Expected Data Structure

After your first training run, you should have:

```
data/
├── checkpoints/
│   ├── checkpoint_ep2.txt
│   ├── checkpoint_ep4.txt
│   └── (possibly more)
├── tensorboard/
│   └── events.out.tfevents.{timestamp}.{hostname}
├── logs/
│   └── training_{timestamp}.log (if logging to file)
├── sessions/
│   └── (may be populated if session storage is active)
└── knowledge_base.db
    └── mechanics table (may have learned patterns)
```

---

## Understanding the Data

### Checkpoints (`data/checkpoints/`)
Text files containing episode statistics:
- Episode number
- Total actions taken
- Success/failure counts
- Time elapsed
- Loop detection events

### TensorBoard Data (`data/tensorboard/`)
Binary event logs for visualization:
- Scalar metrics (rewards, episode length)
- Training progress over time
- Action distribution
- Success rates

### Knowledge Base (`data/knowledge_base.db`)
SQLite database with tables:
- `mechanics`: Learned game rules and patterns
- (Future: `sessions`, `experiences`, `strategies`)

### Training Logs (`data/logs/`)
Detailed JSON-formatted logs:
- Every action taken
- Vision system outputs
- Safety validation results
- Error messages and warnings

---

## What the Agent Does (Current State)

**Vision**: ✅ Working
- Captures game screen every step
- Extracts text with OCR (12+ regions typically)
- No YOLO detections yet (model not trained)
- Detects color regions

**Decision Making**: ⚠️ Random Exploration
- No trained RL model yet
- Uses random action selection
- Mostly WAIT actions (safe default)
- Learning what's possible

**Safety**: ✅ Working
- Validates all actions before execution
- Checks window bounds
- Enforces action blacklist
- Rate limiting active

**Execution**: ✅ Working
- Simulates mouse clicks
- Keyboard input
- Timing delays

---

## Next Steps After Data Collection

### 1. Review What Was Collected
```bash
# Quick stats
echo "Checkpoints: $(ls data/checkpoints/ | wc -l)"
echo "TensorBoard files: $(ls data/tensorboard/ | wc -l)"

# View first checkpoint
head -20 data/checkpoints/checkpoint_ep2.txt
```

### 2. Visualize with TensorBoard
```bash
tensorboard --logdir data/tensorboard --host localhost --port 6006
# Open browser to: http://localhost:6006
```

Look for:
- Episode length trends
- Action distribution
- Success/failure rates

### 3. Analyze Game State Captures
The agent captured screenshots and extracted text. Review logs to see:
- What text was detected
- Where clicks were attempted
- What UI elements were visible

### 4. Plan RL Model Training
Once you have enough data (100+ episodes recommended):
- Prepare experience replay buffer
- Train RL model on collected experiences
- Next training run will use trained model instead of random actions

### 5. Label Data for YOLO Training
- Extract representative screenshots
- Label UI elements (cards, buttons, timers)
- Train YOLO detection model
- Enable YOLO in next training run

---

## Troubleshooting

### "Window not active" errors
**Solution**: Click on Cultist Simulator window to make it active

### Agent only does WAIT actions
**Expected**: This is normal for untrained agent. It's being cautious.

### No checkpoint files created
**Check**: 
- Did training complete all episodes?
- Check `--checkpoint` parameter (must be ≤ total episodes)
- Look for errors in terminal output

### Permission denied
**Solution**: Grant Screen Recording permission
1. System Settings → Privacy & Security → Screen Recording
2. Enable Terminal and Python
3. Restart terminal
4. Try again

---

## Emergency Stop

If anything goes wrong:

1. **Keyboard shortcut**: Press **Cmd+Shift+Q** (works even when agent has mouse control)
2. **Terminal**: Press **Ctrl+C** 
3. **Force quit**: Activity Monitor → Find Python process → Force Quit

The agent will stop gracefully and save progress.

---

## Ready to Start? 🎯

**Run this now**:
```bash
./quick_train.sh
```

Or if you prefer the full command:
```bash
source venv/bin/activate && python3 -m src.orchestrator.cli train \
  --agent-id first_training_$(date +%Y%m%d_%H%M%S) \
  --episodes 5 \
  --max-actions 10 \
  --checkpoint 2 \
  --window "Cultist Simulator" \
  --verbose
```

**Estimated time**: 2-3 minutes  
**Data generated**: 2-3 checkpoints, TensorBoard metrics, session records

Let the training begin! 🚀
