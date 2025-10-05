# How to Stop/Pause the Agent

The Cultist Simulator AI Agent supports graceful interruption. Here are the ways to stop the agent:

## Method 1: Keyboard Interrupt (Ctrl+C)

**Recommended for most users**

Press `Ctrl+C` in the terminal while the agent is running:

```bash
python -m src.orchestrator.agent_runner --window-name "Cultist Simulator" --max-actions 100

# Press Ctrl+C to stop
```

**What happens:**
1. Agent detects the interrupt signal
2. Completes the current action (if executing)
3. Saves session data to database
4. Logs final metrics
5. Exits cleanly with exit code 0

**Notes:**
- First `Ctrl+C`: Graceful stop (saves data)
- Second `Ctrl+C`: Force quit (may lose current session data)
- The agent prints a confirmation message when interrupt is received

## Method 2: Test Script with Interrupt Support

Use the provided test script:

```bash
cd /Users/stan/Documents/Programming/cultist-simulator
source venv/bin/activate
python test_interrupt.py

# Press Ctrl+C when you want to stop
```

This script shows a clear status message and demonstrates the interrupt handling.

## Method 3: Emergency Stop (Programmatic)

For scripts/automation, you can trigger emergency stop programmatically:

```python
from src.automation import request_emergency_stop

# In another thread or signal handler:
request_emergency_stop()
```

This sets a global flag that the agent checks every iteration.

## Method 4: Max Actions Limit

Set a maximum number of actions when starting the agent:

```bash
python -m src.orchestrator.agent_runner \
  --window-name "Cultist Simulator" \
  --max-actions 50  # Agent stops after 50 actions
```

## Method 5: Max Duration Limit

Set a maximum time duration:

```bash
python -m src.orchestrator.agent_runner \
  --window-name "Cultist Simulator" \
  --max-actions 1000 \
  --max-duration 300  # Stop after 5 minutes (300 seconds)
```

## Method 6: Window Focus Lost

The agent automatically pauses when the game window loses focus:

1. Click on another application window
2. Agent detects focus loss and pauses
3. Agent waits for window to regain focus
4. Resume by clicking back on Cultist Simulator window

**Safety feature**: Prevents accidental interaction with other applications

## What Gets Saved on Stop

When you interrupt the agent (via any method), it saves:

- ✅ All actions taken in the session
- ✅ Session duration and timestamp
- ✅ End condition (manual_stop, timeout, etc.)
- ✅ Agent metrics (success rate, loop detection, etc.)
- ✅ Session ID for later replay/analysis

**Database location**: `data/knowledge_base.db`

## Checking Saved Sessions

After stopping, you can check saved sessions:

```python
from src.learning import get_all_sessions

sessions = get_all_sessions()
for session in sessions[-5:]:  # Last 5 sessions
    print(f"Session {session.session_id}: {session.total_actions} actions, {session.duration_seconds:.1f}s")
```

## Quick Test

To verify interrupt handling works:

```bash
# Terminal 1: Run agent
python test_interrupt.py

# Wait a few seconds for agent to start executing actions

# Press Ctrl+C

# You should see:
# ⚠️  Interrupt received (Ctrl+C). Stopping agent gracefully...
# ✅ INTERRUPT HANDLED SUCCESSFULLY
```

## Troubleshooting

**Problem**: Agent doesn't stop when pressing Ctrl+C

**Solutions**:
1. Make sure terminal has focus (click on terminal window)
2. Press Ctrl+C twice (second press forces quit)
3. Use `pkill -INT python` in another terminal
4. Force kill: `pkill -9 python` (last resort, may lose data)

**Problem**: Agent stops but session data not saved

**Cause**: You pressed Ctrl+C twice (force quit)

**Solution**: Press Ctrl+C only once and wait for graceful shutdown

## Example Usage

```bash
# Start agent with reasonable limits
python -m src.orchestrator.agent_runner \
  --window-name "Cultist Simulator" \
  --max-actions 100 \
  --test-mode

# Let it run for a while...
# Press Ctrl+C when you want to stop

# Check the logs:
ls -lt data/logs/agent_*.jsonl | head -1  # Most recent log

# Or check sessions in database:
python -c "from src.learning import get_all_sessions; print(len(get_all_sessions()))"
```

---

**Summary**: The agent supports multiple safe stop methods. `Ctrl+C` is the most convenient for interactive use. All methods ensure session data is saved before exiting.
