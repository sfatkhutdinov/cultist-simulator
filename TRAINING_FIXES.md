# Training Script Fixes Applied

## Date: October 5, 2025

## Issues Found and Fixed

### 🐛 Issue #1: Duplicate TensorBoard Launch
**Problem**: 
- Bash script launches TensorBoard
- Python code also tries to launch TensorBoard
- Second launch fails because port 6006 is already in use
- Training aborts with: `Failed to start TensorBoard: TensorBoard process terminated unexpectedly`

**Root Cause**:
```bash
# start_training.sh launches TensorBoard
tensorboard --logdir data/tensorboard --host localhost --port 6006

# Then Python CLI also tries to launch it
launch_tensorboard_in_safari(tensorboard_dir, verbose=args.verbose)
# ❌ Conflict! Port already in use
```

**Fix Applied**:
Added `--no-tensorboard` flag to both bash scripts to skip Python's TensorBoard launch:

```bash
# start_training.sh
python3 -m src.orchestrator.cli train \
  --no-tensorboard \  # ← ADDED THIS
  --verbose
  
# quick_train.sh  
python3 -m src.orchestrator.cli train \
  --no-tensorboard \  # ← ADDED THIS
  --verbose
```

**Result**: ✅ Bash script manages TensorBoard, Python code skips launch

---

### 🐛 Issue #2: Max Actions Ignored
**Problem**:
- Bash script specifies `--max-actions 150`
- Python code ignores it and uses config file default (30)
- Episodes end too early (after only 30 actions instead of 150)

**Root Cause**:
```python
# cli.py line 221 (OLD CODE)
max_actions = config.get('learning', {}).get('max_actions_per_episode', 
                                              getattr(args, 'max_actions', 30))
# ❌ Config file always wins, CLI arg never used
```

**Fix Applied**:
Changed logic to prioritize CLI arguments over config file:

```python
# NEW CODE
if hasattr(args, 'max_actions') and args.max_actions != 1000:
    # User explicitly set max-actions (not using default)
    max_actions = args.max_actions  # ← Use CLI arg
else:
    # Use config file or default
    max_actions = config.get('learning', {}).get('max_actions_per_episode', 30)
```

**Result**: ✅ CLI arguments now override config file settings

---

## Files Modified

### 1. `start_training.sh`
- Added `--no-tensorboard` flag to prevent duplicate TensorBoard launch

### 2. `quick_train.sh`
- Added `--no-tensorboard` flag to prevent duplicate TensorBoard launch

### 3. `src/orchestrator/cli.py`
- Fixed max_actions logic to prioritize CLI arguments over config file

---

## Verification

### Test #1: TensorBoard Launch
```bash
./start_training.sh
# Expected output:
# ✓ TensorBoard running at http://localhost:6006
# (No errors about TensorBoard failing)
```

### Test #2: Max Actions Respected
```bash
./start_training.sh
# Expected in output:
# Max actions per episode: 150  (not 30)
```

### Test #3: Training Runs Successfully
```bash
./quick_train.sh
# Expected:
# - 5 episodes complete
# - ~20 actions per episode (not stopping at 10 or 30)
# - TensorBoard shows metrics
# - No errors
```

---

## How It Works Now

### Startup Sequence (Correct Flow):
```
1. start_training.sh runs
   ├─ Activates venv
   ├─ Kills old TensorBoard (if any)
   ├─ Starts fresh TensorBoard on port 6006
   ├─ Waits 2 seconds for initialization
   └─ Shows: "✓ TensorBoard running at http://localhost:6006"

2. Python CLI starts
   ├─ Sees --no-tensorboard flag
   ├─ Skips TensorBoard launch (already running)
   ├─ Sees --max-actions 150
   ├─ Uses 150 (not config's 30)
   └─ Begins training with correct parameters

3. Training proceeds
   ├─ Logs metrics to TensorBoard
   ├─ Runs up to 150 actions per episode
   └─ Completes successfully
```

---

## Parameter Priority (After Fix)

### Max Actions Decision Tree:
```
1. Did user specify --max-actions on command line?
   ├─ Yes, and it's not the default (1000) → Use CLI value ✅
   └─ No, or it's the default → Use config file value

Examples:
  --max-actions 150  → Uses 150 ✅
  --max-actions 50   → Uses 50 ✅
  (no flag)          → Uses config (30)
```

### TensorBoard Decision Tree:
```
1. Did bash script already start TensorBoard?
   ├─ Yes, and --no-tensorboard flag set → Skip Python launch ✅
   └─ No flag → Python tries to launch (will conflict!)

With our scripts:
  start_training.sh   → Bash launches TB, Python skips ✅
  quick_train.sh      → Bash launches TB, Python skips ✅
  Manual CLI usage    → Python launches TB (normal behavior)
```

---

## Testing Instructions

### Quick Test (3 minutes):
```bash
# Make sure Cultist Simulator is running
./quick_train.sh

# Expected output:
# ✓ TensorBoard running at http://localhost:6006
# Max actions per episode: 20
# Episodes complete without errors
```

### Production Test (1-2 hours):
```bash
# Make sure Cultist Simulator is running
./start_training.sh

# Expected output:
# ✓ TensorBoard running at http://localhost:6006
# Max actions per episode: 150
# Training proceeds for 200 episodes
```

### Verify TensorBoard:
```bash
# Open browser to:
http://localhost:6006

# Should see:
# - Episode metrics graphs
# - Data updating as training progresses
# - No "No data" errors
```

---

## Troubleshooting

### If TensorBoard still fails:
```bash
# Check if port is in use
lsof -i :6006

# Kill any existing TensorBoard
pkill -f tensorboard

# Try again
./start_training.sh
```

### If max-actions still shows 30:
```bash
# Check config file
cat config/test_agent.yaml

# Verify CLI argument in terminal output
# Should see: "Max actions per episode: 150"
# If it shows 30, check the Python fix was applied
```

### If training aborts immediately:
```bash
# Check logs
tail -50 data/logs/agent_*.jsonl

# Common causes:
# - Window not found (make sure game is running)
# - Permission denied (screen recording permission needed)
# - Config error (check YAML syntax)
```

---

## Summary

✅ **Fixed**: Duplicate TensorBoard launch (bash + Python conflict)  
✅ **Fixed**: Max actions ignored (config overriding CLI args)  
✅ **Result**: Training scripts now work correctly with optimal parameters

**Ready to train!** Just run:
```bash
./start_training.sh
```

Both issues were preventing proper training:
1. Training wouldn't start (TensorBoard error)
2. Episodes too short (30 actions instead of 150)

Now both are resolved! 🚀
