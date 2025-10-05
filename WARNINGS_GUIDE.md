# Training Warnings & What They Mean

This document explains the warnings you might see during training and testing and whether you need to worry about them.

---

## 🧪 Test Suite Warnings (RESOLVED ✅)

### Pytest: 225 External Dependency Warnings

**Status**: ✅ **SUPPRESSED** as of 2025-10-04

**What you saw**:
```
146 passed, 14 skipped, 225 warnings in 55.01s
```

**What it means**:
- All 225 warnings came from external libraries (EasyOCR, PyTorch, Pillow)
- ZERO warnings from our code
- These are deprecation notices for APIs that will change in future library versions

**Breakdown**:
1. **~143 warnings**: PyTorch quantization API deprecation in EasyOCR
2. **~66 warnings**: Pillow `mode` parameter deprecation in EasyOCR  
3. **~16 warnings**: MPS `pin_memory` not supported (Apple Silicon)

**Is this a problem?**
- ❌ **NO** - Everything works perfectly
- These are warnings about future API changes (2026+)
- Our code has zero warnings

**Action taken**:
- Added filters to `pyproject.toml` to suppress known external warnings
- Test output is now clean: `146 passed, 14 skipped in 50.18s`

**To see suppressed warnings** (if curious):
```bash
pytest tests/ -W default -v
```

---

## ✅ Normal (Expected) Warnings

### 1. `rl_model_not_loaded`
```
2025-10-04 21:36:33 [warning] rl_model_not_loaded
```

**What it means:**
- No pre-trained RL (Reinforcement Learning) model exists yet
- Agent defaults to WAIT actions until a model is trained

**Is this a problem?**
- ❌ **NO** - This is expected on first run
- The agent needs to complete training episodes to learn
- After training, this warning will disappear

**Action needed:**
- None - continue training to build the model


### 2. `'pin_memory' not supported on MPS` (SUPPRESSED)
```
UserWarning: 'pin_memory' argument is set as true but not supported on MPS now
```

**What it means:**
- PyTorch/EasyOCR tries to use "pinned memory" for faster data transfer
- Apple's Metal Performance Shaders (MPS) doesn't support this feature yet
- Falls back to regular memory allocation

**Is this a problem?**
- ❌ **NO** - Completely harmless
- OCR still works perfectly fine
- Just slightly slower than it could be with pinned memory

**Action needed:**
- None - warning now suppressed in code (as of 2025-10-04)
- If you see it: ignore it, OCR functionality is unaffected


## ⚠️ Warnings to Watch For

### Window Focus Lost
```
[warning] window_focus_lost window_name=Cultist Simulator
```

**What it means:**
- Game window is no longer active/focused
- Agent cannot interact with unfocused window

**Action needed:**
- Switch back to the game window
- Or stop training and restart when ready


### Rate Limit Exceeded
```
[warning] rate_limit_exceeded actions_per_second=15 max_allowed=10
```

**What it means:**
- Agent is performing actions too quickly
- Safety system throttling to prevent spam

**Action needed:**
- None - automatic throttling will slow down actions
- Review if certain action patterns are looping


### Safety Validation Failed
```
[warning] action_blocked action_type=keypress reason=blacklisted_key
```

**What it means:**
- Agent tried to perform an unsafe action
- Safety system blocked it (working as designed)

**Action needed:**
- None - this is the safety system protecting your system
- Check logs to ensure agent isn't repeatedly trying blocked actions


## 🚨 Actual Errors (Need Attention)

### Screen Capture Failed
```
[error] screen_capture_failed error=...
```

**Action needed:**
- Check if game window exists
- Verify window name matches: "Cultist Simulator"
- Check screen permissions (System Preferences → Privacy → Screen Recording)


### Database Connection Failed
```
[error] database_connection_failed error=...
```

**Action needed:**
- Check if `data/knowledge_base.db` exists
- Run: `python scripts/init_database.py`
- Verify file permissions


### OCR Initialization Failed
```
[error] ocr_initialization_failed error=...
```

**Action needed:**
- Check if EasyOCR is installed: `pip list | grep easyocr`
- Reinstall if needed: `pip install easyocr`
- Ensure enough disk space for OCR models (~500MB)


## Quick Reference

| Warning | Severity | Action |
|---------|----------|--------|
| `rl_model_not_loaded` | 🟢 Normal | None - expected on first run |
| `pin_memory...MPS` | 🟢 Normal | None - suppressed in code |
| `window_focus_lost` | 🟡 Attention | Refocus game window |
| `rate_limit_exceeded` | 🟡 Attention | None - auto-throttled |
| `action_blocked` | 🟡 Attention | Review if repeated |
| `screen_capture_failed` | 🔴 Error | Check window/permissions |
| `database_*_failed` | 🔴 Error | Check DB setup |
| `ocr_*_failed` | 🔴 Error | Check EasyOCR install |


## Tips for Clean Training Output

### Reduce Log Verbosity
Edit `src/lib/logging_config.py` to change log level:
```python
# Show only INFO and above (hide DEBUG)
logging.basicConfig(level=logging.INFO)
```

### Filter Specific Warnings
Add to relevant module:
```python
import warnings
warnings.filterwarnings('ignore', message='pattern to ignore')
```

### Redirect to File
Save logs for later review:
```bash
python -m src.orchestrator.cli train --episodes 100 2>&1 | tee training.log
```

### Watch Only Errors
Filter output in real-time:
```bash
python -m src.orchestrator.cli train --episodes 100 2>&1 | grep -E "(error|ERROR|Error)"
```


## Training is Working If You See:

✅ `training_started`
✅ `training_episode_start`
✅ `game_state_captured`
✅ `text_extraction_complete`
✅ `session_stored`
✅ `training_episode_complete`
✅ `checkpoint_saved`
✅ `training_completed`

Don't worry about warnings unless they prevent training from completing!
