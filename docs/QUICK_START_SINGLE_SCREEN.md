# 🎮 Single-Screen Usage - Quick Reference

## ✅ Pre-Flight Checklist

Before running the agent on a single-screen Mac:

1. **Open Cultist Simulator**
   - Launch the game
   - Start a new game or load save
   
2. **Make Game Window Active**
   - Click on the Cultist Simulator window
   - Ensure it's the foreground application
   
3. **Grant macOS Permissions** (first time only)
   - System Settings → Privacy & Security → Screen Recording
   - System Settings → Privacy & Security → Accessibility
   - Enable for Terminal (or your IDE)

4. **Start Agent**
   ```bash
   python -m src.orchestrator.cli run \
     --agent-id my_agent \
     --window "Cultist Simulator" \
     --max-actions 100  # Limit actions for testing
   ```

## 🛡️ Safety Features Active

When agent is running:

| Feature | Status | What It Does |
|---------|--------|--------------|
| **Window Focus Check** | ✅ Active | Verifies game window is focused before starting |
| **Continuous Monitoring** | ✅ Active | Pauses if window loses focus |
| **Boundary Validation** | ✅ Active | All clicks checked against window bounds |
| **Keyboard Blacklist** | ✅ Active | Cmd+Q, Cmd+W, etc. blocked |
| **Violation Logging** | ✅ Active | All safety events logged to file |
| **Emergency Stop** | ✅ Active | Ctrl+C or F12 stops immediately |

## 🎯 What You'll See

**Normal Operation:**
```
INFO: active_window_verified window_name=Cultist Simulator bounds=Rect(...)
INFO: episode_started session_id=abc123 episode_number=1
DEBUG: step_vision_start
DEBUG: step_action_selection
INFO: click_executed point=Point(x=450, y=300)
```

**Window Loses Focus:**
```
WARNING: window_lost_focus window_name=Cultist Simulator
INFO: episode_paused waiting_for_focus
```

**Safety Violation Blocked:**
```
WARNING: action_blocked_bounds point=Point(x=2000, y=100) outside bounds
WARNING: safety_violation_logged violation_type=OUT_OF_BOUNDS
```

## 🚨 Emergency Stop

**How to stop the agent immediately:**

1. **Keyboard:** Press `Ctrl+C` in terminal
2. **Code:** Call `request_emergency_stop()`
3. **Automatic:** Switch to another app (agent pauses)

**What happens:**
- All automation stops within 1 action loop (~100ms)
- Current session is saved
- State is written to disk
- Logs record stop reason

## 🔍 Monitoring

**Watch logs in real-time:**
```bash
# Main agent logs
tail -f data/logs/agent_*.jsonl

# Safety violations
tail -f data/logs/safety_violations.jsonl
```

**Check window bounds:**
```bash
python -c "
from src.automation.window_manager import get_active_window_bounds
bounds = get_active_window_bounds('Cultist Simulator')
print(f'Window bounds: {bounds}')
"
```

## ❓ Troubleshooting

### "Window is not active" Error

**Symptoms:** Agent refuses to start
```
ERROR: Window 'Cultist Simulator' is not active!
```

**Solutions:**
1. Click on game window to focus it
2. Verify window title matches exactly
3. Check if game is minimized (restore it)
4. Retry agent command

### Agent Clicks Outside Game

**Symptoms:** Should never happen (blocked by safety)

**If it does happen:**
1. **Stop immediately** (Ctrl+C)
2. Check `data/logs/safety_violations.jsonl`
3. Report bug with logs
4. This indicates a critical safety failure

### Agent Doesn't Resume After Focus Returns

**Symptoms:** Agent stays paused after clicking game window

**Solutions:**
1. Check logs for errors: `tail -f data/logs/agent_*.jsonl`
2. Verify window name: might have changed
3. Restart agent
4. Check macOS permissions still granted

## 📊 Validation Commands

**Test window detection:**
```bash
python -m src.automation.cli check-window --window "Cultist Simulator"
```

**Test safety validation:**
```bash
python -m src.safety.cli check-bounds --x 500 --y 300
```

**Test full pipeline (dry run):**
```bash
python -m src.orchestrator.cli run \
  --agent-id test \
  --window "Cultist Simulator" \
  --max-actions 10 \
  --dry-run
```

## ⚡ Quick Tips

1. **First run:** Use `--max-actions 10` to limit initial test
2. **Monitor closely:** Watch terminal output for first few minutes
3. **Test emergency stop:** Try Ctrl+C once to verify it works
4. **Check bounds:** Ensure window bounds match your screen
5. **Log everything:** Keep logs for troubleshooting

## 📝 Example Session

```bash
# 1. Start game
open -a "Cultist Simulator"

# 2. Wait for game to load and click window
# (Game window is now active)

# 3. Run agent with safety limits
python -m src.orchestrator.cli run \
  --agent-id test_run \
  --window "Cultist Simulator" \
  --max-actions 50 \
  --max-duration 300

# Expected output:
# ✓ active_window_verified
# ✓ episode_started  
# ✓ agent running with boundary enforcement
# ... (50 actions within game window)
# ✓ episode_complete

# 4. Review logs
cat data/logs/safety_violations.jsonl
# (Should be empty or only warnings, no errors)
```

## 🎓 Advanced Usage

**Train agent overnight safely:**
```bash
# Use screen/tmux for persistent session
screen -S cultist_agent

python -m src.orchestrator.cli train \
  --agent-id overnight_v1 \
  --window "Cultist Simulator" \
  --num-episodes 500 \
  --max-actions 1000

# Detach: Ctrl+A, D
# Reattach: screen -r cultist_agent
```

**Multi-episode with checkpointing:**
```bash
python -m src.orchestrator.cli train \
  --agent-id checkpoint_v1 \
  --window "Cultist Simulator" \
  --num-episodes 100 \
  --checkpoint-every 10 \
  --save-replays
```

---

**Remember:** The agent is designed to be safe by default. All the safety features are automatic - you just need to ensure the game window is focused when starting! 🛡️
