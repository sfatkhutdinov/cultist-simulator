# End-to-End Testing Guide
**Task T134**: Run E2E test with actual Cultist Simulator game

## Overview

The end-to-end (E2E) test validates that the AI agent can:
- ✅ Capture game state from running Cultist Simulator
- ✅ Detect UI elements and text
- ✅ Select appropriate actions
- ✅ Execute actions safely within the game window
- ✅ Run for 10+ actions without crashing
- ✅ Log all interactions for replay/analysis

## Prerequisites

### 1. Game Setup
- **Install Cultist Simulator** (Steam or standalone)
- **Launch the game** and get to the main menu or a playable state
- **Keep the game window visible** (don't minimize)

### 2. macOS Permissions
The agent needs Screen Recording permission to capture the game window:

1. Open **System Settings** → **Privacy & Security** → **Screen Recording**
2. Enable screen recording for:
   - `Terminal` (if running from terminal)
   - `Python` or `Python3`
   - Your IDE (if running from VS Code, PyCharm, etc.)
3. **Restart your terminal/IDE** after granting permissions

### 3. Python Environment
```bash
# Activate virtual environment
source venv/bin/activate

# Verify all dependencies installed
pip install -r requirements.txt
```

## Quick Start

### Step 1: Find the Game Window

Run the window finder helper:
```bash
python3 scripts/find_window.py
```

This will test common window names and show you which one works.

**Example output:**
```
Testing: 'Cultist Simulator'...
   ✅ FOUND: Rect(x=0, y=23, width=1920, height=1057)

To run E2E test:
   python3 scripts/test_e2e.py --window "Cultist Simulator"
```

### Step 2: Run the E2E Test

```bash
# Basic test (10 actions)
python3 scripts/test_e2e.py

# Custom number of actions
python3 scripts/test_e2e.py --actions 20

# With specific window name
python3 scripts/test_e2e.py --window "Cultist Simulator"

# Dry run (test without clicking - safety test)
python3 scripts/test_e2e.py --dry-run

# Verbose output
python3 scripts/test_e2e.py --verbose
```

## Test Execution

### What Happens During the Test

1. **Prerequisites Check**
   - Verifies game window exists
   - Checks window bounds
   - Confirms window focus

2. **Test Cycle** (repeated for N actions):
   - Capture game screenshot
   - Detect UI elements (YOLO + OCR)
   - Select action based on game state
   - Validate action with safety system
   - Execute action (click/keypress)
   - Wait 1 second (safety delay)
   - Log all data

3. **Report Generation**
   - Statistics summary
   - Performance metrics
   - Error log (if any)
   - Session data saved for replay

### Expected Output

```
============================================================
END-TO-END TEST - Cultist Simulator AI Agent
============================================================
Window: Cultist Simulator
Target Actions: 10
Dry Run: False
============================================================

Checking prerequisites...
✅ Found game window: Rect(x=0, y=23, width=1920, height=1057)
✅ Window is focused
✅ Prerequisites passed. Starting test...

============================================================
Test Cycle 1/10
============================================================
Capturing game state...
✅ Captured game state in 287.43ms
   Detected 5 elements
   Extracted 12 text regions
Selecting action...
✅ Selected action: Action(CLICK, point=Point(500, 300))
✅ Action validated by safety system
Executing action...
✅ Action executed successfully in 32.15ms
⏱️  Waiting 1.0s before next action...

[... cycles 2-10 ...]

============================================================
TEST REPORT
============================================================

📊 Statistics:
   Actions Executed: 10/10
   Actions Blocked:  0
   Errors:           0

⏱️  Performance:
   Avg Vision Capture: 312.45ms
   ✅ Vision meets NFR-001 (<500ms)

💾 Session saved to: data/sessions/e2e_test_20251004_223015.json

============================================================
✅ END-TO-END TEST PASSED
============================================================
```

## Success Criteria

The test is considered **PASSED** if:
- ✅ At least 10 actions are executed
- ✅ No critical errors occur
- ✅ All safety checks pass
- ✅ Vision pipeline completes in <500ms
- ✅ Actions execute within game window bounds

## Troubleshooting

### Issue: "Game window not found"

**Solutions:**
1. Verify game is running: `ps aux | grep -i cultist`
2. Check window title in menu bar (top of screen)
3. Try different window names:
   ```bash
   python3 scripts/test_e2e.py --window "Unity Player"
   python3 scripts/test_e2e.py --window "Cultist Simulator - Unity"
   ```
4. Use the window finder: `python3 scripts/find_window.py`

### Issue: "Permission denied" or blank screenshots

**Solutions:**
1. Grant Screen Recording permissions (see Prerequisites above)
2. Restart terminal after granting permissions
3. Try running with sudo (not recommended): `sudo python3 scripts/test_e2e.py`
4. Check permissions: System Settings → Privacy & Security → Screen Recording

### Issue: "Window is not focused"

**Solutions:**
1. Click on the game window
2. Don't switch to other windows during the test
3. Run in `--dry-run` mode first to test without interaction

### Issue: Actions click in wrong locations

**Possible causes:**
1. **Multiple displays**: Game on secondary monitor
   - Move game to primary monitor
   - Check window bounds in test output
   
2. **Display scaling**: Retina/HiDPI displays
   - This should be handled automatically
   - If issues persist, check Rect coordinates in logs

3. **Game resolution**: Different from expected
   - Supported: 1920x1080, 2560x1440, 3840x2160
   - Use fullscreen or windowed fullscreen mode

### Issue: Test crashes or hangs

**Solutions:**
1. Check logs in `data/logs/` for error details
2. Run with `--verbose` for detailed output
3. Start with fewer actions: `--actions 5`
4. Use `--dry-run` to test detection without clicking
5. Check CPU/memory usage - close other apps

## Dry Run Mode

Test the vision pipeline without executing actions:

```bash
python3 scripts/test_e2e.py --dry-run
```

This is useful for:
- Verifying window detection
- Testing vision pipeline performance
- Checking action selection logic
- Ensuring safety validation works
- Running tests without risking game state

## Session Replay

All test sessions are saved to `data/sessions/`. Each session includes:
- All actions attempted
- Success/failure status
- Vision capture timing
- Errors encountered
- Full game state snapshots (if enabled)

View session data:
```bash
cat data/sessions/e2e_test_20251004_223015.json | python3 -m json.tool
```

## Advanced Options

### Custom Configuration

Create a test config file `config/e2e_test.yaml`:
```yaml
window_name: "Cultist Simulator"
max_actions: 50
action_delay_sec: 2.0
safety_checks:
  bounds_validation: true
  rate_limiting: true
  blacklist_keys: true
vision:
  capture_timeout_ms: 1000
  detection_confidence: 0.6
```

Use config:
```bash
python3 scripts/test_e2e.py --config config/e2e_test.yaml
```

### Performance Profiling

Enable detailed performance tracking:
```bash
python3 scripts/test_e2e.py --profile --actions 50
```

Generates:
- Per-action timing breakdown
- Vision pipeline bottlenecks
- Action selection performance
- Safety validation overhead

## Safety Features

The E2E test includes multiple safety layers:

1. **Bounds Validation**: All clicks within game window
2. **Rate Limiting**: 1 second minimum between actions
3. **Blacklist Keys**: No Cmd+Q, Cmd+W, etc.
4. **Window Focus**: Only acts when game is focused
5. **Emergency Stop**: Press F12 to halt execution
6. **Dry Run Mode**: Test without actual interaction

## Next Steps After E2E Test

Once the E2E test passes:

1. **T134a**: Multi-resolution testing
2. **T135**: Adversarial safety testing
3. **T136**: Code cleanup
4. **T137**: Final linting and type checking

Then proceed to:
- Extended training runs (100+ episodes)
- Different game scenarios
- Performance optimization if needed
- Production deployment

## Files Created

- `scripts/test_e2e.py` - Main E2E test runner
- `scripts/find_window.py` - Window detection helper
- `E2E_TESTING_GUIDE.md` - This guide
- `data/sessions/e2e_test_*.json` - Test session logs

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs in `data/logs/`
3. Run with `--verbose` for detailed output
4. Try `--dry-run` mode first
5. Check that all 146 unit tests still pass: `pytest`

---

**Remember**: The E2E test interacts with the actual game. Start with `--dry-run` mode and a small number of actions (`--actions 5`) to verify everything works before running longer tests.
