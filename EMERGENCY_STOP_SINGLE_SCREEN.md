# Emergency Stop - Single Screen Users

## The Problem

On a single-screen MacBook, when the AI agent is running, it controls your mouse. This makes it **impossible to click on the terminal to press Ctrl+C** to stop it.

## The Solution: Cmd+Shift+Q

Press **Cmd+Shift+Q** from anywhere - even while the agent is moving your mouse!

```
🛑 EMERGENCY STOP HOTKEY: Cmd+Shift+Q
```

This works because it's a **global keyboard listener** that runs in the background, independent of mouse position or window focus.

## How It Works

1. **Start the agent** (any method):
   ```bash
   python test_interrupt.py
   # or
   python -m src.orchestrator.agent_runner --window-name "Cultist Simulator" --max-actions 100
   ```

2. **You'll see this message**:
   ```
   ⚡ Emergency Stop Active: Press Cmd+Shift+Q to stop agent from anywhere
   ```

3. **When you want to stop**:
   - Press `Cmd+Shift+Q` (even while agent moves mouse)
   - Agent detects the keypress immediately
   - Current action completes safely
   - Session data is saved
   - Agent exits cleanly

4. **You'll see confirmation**:
   ```
   ======================================================================
   🛑 EMERGENCY STOP TRIGGERED (Cmd+Shift+Q)
   ======================================================================
     Stopping agent immediately...
   ======================================================================
   ```

## Why Cmd+Shift+Q?

- **Not used by system**: Won't quit apps or conflict with macOS shortcuts
- **Easy to remember**: Similar to Cmd+Q (quit) but safer
- **Two-handed**: Reduces accidental triggers
- **Works anywhere**: Global listener catches it regardless of focus

## Alternative Stop Methods

If Cmd+Shift+Q doesn't work:

1. **Force quit terminal** (last resort):
   - Press `Cmd+Option+Esc`
   - Select Terminal
   - Click "Force Quit"
   - ⚠️ May lose current session data

2. **Switch workspace and use terminal**:
   - Press `Ctrl+→` to switch to another desktop
   - Open new terminal window
   - Run: `pkill -INT python`

3. **Use second device**:
   - SSH from another computer
   - Run: `pkill -INT python`

## Troubleshooting

**Q: Cmd+Shift+Q doesn't work**

A: Check these:
1. Make sure you saw the "Emergency Stop Active" message at startup
2. Try pressing the keys again (hold Cmd+Shift, then tap Q)
3. Check that pynput is installed: `pip show pynput`
4. Grant accessibility permissions if macOS prompts

**Q: macOS asks for accessibility permissions**

A: 
1. Click "Open System Preferences"
2. Go to Security & Privacy → Privacy → Accessibility
3. Click the lock to make changes
4. Check the box next to Terminal or Python
5. Restart the agent

**Q: Agent stops but session not saved**

A: This shouldn't happen with Cmd+Shift+Q (it's graceful). If it does:
- Check `data/knowledge_base.db` for your session
- Look in `data/logs/` for error messages

## Testing the Emergency Stop

Quick test to verify it works:

```bash
cd /Users/stan/Documents/Programming/cultist-simulator
source venv/bin/activate
python test_interrupt.py

# Wait for "Emergency Stop Active" message
# Let agent run for a few seconds
# Press Cmd+Shift+Q
# Verify you see the "EMERGENCY STOP TRIGGERED" message
```

## Technical Details

- Uses `pynput` library for global keyboard monitoring
- Listener runs in background daemon thread
- Monitors for Cmd+Shift+Q combination
- Sets emergency stop flag when detected
- Agent checks flag every iteration (~0.5s)
- Graceful shutdown preserves all session data

## For Multi-Screen Users

If you have multiple screens, you can also use:
- **Ctrl+C in terminal** (traditional method)
- **Cmd+Shift+Q** (works too, your choice!)

## Summary

**Single screen? → Use Cmd+Shift+Q**

It's the only reliable way to stop the agent when it controls your mouse. The hotkey works from anywhere, anytime, and ensures your session data is safely saved.

---

**Last Updated**: October 5, 2025  
**Agent Version**: v0.9.0 with emergency stop listener
