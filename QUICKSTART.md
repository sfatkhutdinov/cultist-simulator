# Quick Start Guide - Cultist Simulator AI Agent

**Last Updated**: October 4, 2025  
**Status**: Production Ready

Get your autonomous AI agent up and running in minutes!

---

## Prerequisites

### System Requirements
- **OS**: macOS 10.14+ (Mojave or later)
- **Python**: 3.11 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB for models and data
- **Game**: Cultist Simulator (Steam or standalone)

### macOS Permissions
You'll need to grant permissions for:
1. **Screen Recording** (for vision system)
2. **Accessibility** (for input simulation - optional)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/sfatkhutdinov/cultist-simulator.git
cd cultist-simulator
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `opencv-python` - Computer vision
- `ultralytics` - YOLO object detection
- `easyocr` - Text extraction
- `sentence-transformers` - NLP embeddings
- `stable-baselines3` - Reinforcement learning
- `pyobjc` - macOS automation
- `pytest` - Testing framework

**Installation time**: ~5-10 minutes (downloads ML models)

### Step 4: Initialize Database

```bash
python3 scripts/init_database.py
```

Creates `data/knowledge_base.db` with schema for:
- Game mechanics
- Session history
- Performance metrics
- Strategies

### Step 5: Verify Installation

```bash
# Run tests
pytest

# Check all 146 tests pass
# Expected: 146 passed, 14 skipped
```

---

## Configuration

### Grant macOS Permissions

1. **Open System Settings** → **Privacy & Security** → **Screen Recording**
2. **Enable** for:
   - Terminal
   - Python
   - Your IDE (VS Code, PyCharm, etc.)
3. **Restart** your terminal/IDE

### Configure for Your Setup

Edit `config/test_agent.yaml`:

```yaml
agent:
  id: "my_agent"
  window_name: "Cultist Simulator"  # Adjust if different
  
vision:
  capture_timeout_ms: 1000
  detection_confidence: 0.6
  
safety:
  bounds_validation: true
  rate_limiting: true
  max_actions_per_second: 2
  blacklisted_keys:
    - "cmd+q"
    - "cmd+w"
    
learning:
  exploration_rate: 0.3
  learning_rate: 0.0003
```

---

## Quick Test

### 1. Find Game Window

```bash
# Launch Cultist Simulator first!
python3 scripts/find_window.py
```

Example output:
```
Testing: 'Cultist Simulator'...
   ✅ FOUND: Rect(x=0, y=23, width=1920, height=1057)

To run E2E test:
   python3 scripts/test_e2e.py --window "Cultist Simulator"
```

### 2. Dry Run Test (Safe)

```bash
python3 scripts/test_e2e.py --dry-run --actions 5
```

This tests vision and action selection **without clicking** anything.

### 3. Live Test

```bash
python3 scripts/test_e2e.py --actions 10
```

Executes 10 real actions in the game!

**Success Criteria**: 10/10 actions executed without errors

---

## Usage Examples

### Basic Vision Test

```python
from src.vision import capture_game_state, get_window_bounds

# Get window
bounds = get_window_bounds("Cultist Simulator")
print(f"Window: {bounds}")

# Capture state
game_state = capture_game_state("Cultist Simulator")
print(f"Elements: {len(game_state.elements)}")
print(f"Text regions: {len(game_state.text_regions)}")
```

### Safe Action Execution

```python
from src.vision import capture_game_state
from src.learning import select_action
from src.safety import validate_action
from src.automation import simulate_click

# Capture state
game_state = capture_game_state("Cultist Simulator")

# Select action
action = select_action(game_state)

# Validate safety
validation = validate_action(
    {"action_type": action.action_type, "point": action.parameters["point"]},
    {"window_bounds": bounds, "window_focused": True}
)

if validation.is_allowed:
    # Execute
    result = simulate_click(
        action.parameters["point"],
        "left",
        bounds
    )
    print(f"Action executed: {result.success}")
else:
    print(f"Action blocked: {validation.blocked_reason}")
```

### Training Run

```python
from src.orchestrator.agent_runner import AgentRunner

# Create runner
runner = AgentRunner(
    agent_id="cultist_agent_001",
    window_name="Cultist Simulator",
    max_actions_per_episode=100
)

# Run training
runner.run_training_loop(num_episodes=50)

# Check metrics
metrics = runner.get_performance_metrics()
print(f"Win rate: {metrics.win_rate:.2%}")
print(f"Avg survival: {metrics.avg_survival_time:.1f}s")
```

---

## CLI Tools

All libraries have CLI interfaces:

### Vision CLI
```bash
# Capture screenshot
python3 -m src.vision.cli capture --window "Cultist Simulator"

# Detect elements
python3 -m src.vision.cli detect --window "Cultist Simulator"

# Extract text
python3 -m src.vision.cli ocr --window "Cultist Simulator"
```

### Automation CLI
```bash
# Simulate click
echo '{"point": {"x": 100, "y": 100}, "button": "left"}' | \
  python3 -m src.automation.cli click --window "Cultist Simulator"

# Simulate key press
echo '{"key": "space"}' | \
  python3 -m src.automation.cli keypress --window "Cultist Simulator"
```

### Safety CLI
```bash
# Validate action
echo '{"action_type": "CLICK", "point": {"x": 100, "y": 100}}' | \
  python3 -m src.safety.cli validate --bounds "0,0,1920,1080"
```

### NLP CLI
```bash
# Analyze narrative
echo '{"text": "You must find the Key of Dreams"}' | \
  python3 -m src.nlp.cli analyze

# Extract goals
echo '{"text": "Seek the hidden chamber"}' | \
  python3 -m src.nlp.cli goals
```

### Learning CLI
```bash
# Query knowledge base
python3 -m src.learning.cli query --mechanic "card_crafting"

# Store session
cat session_data.json | python3 -m src.learning.cli store
```

---

## Performance

Your system should meet these benchmarks:

| Component | Target | Actual |
|-----------|--------|--------|
| Vision Capture | <500ms | ~300ms |
| Knowledge Query | <100ms | <1ms |
| Safety Validation | <10ms | <0.1ms |
| Action Selection | N/A | <0.01ms |

Run performance profiling:
```bash
python3 scripts/profile_performance.py
```

---

## Troubleshooting

### "Window not found"
- Verify game is running
- Check window title matches (use `find_window.py`)
- Try window name variations

### "Permission denied" errors
- Grant Screen Recording permissions
- Restart terminal after granting
- Check System Settings → Privacy & Security

### Tests failing
```bash
# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_vision.py -v

# Check for missing dependencies
pip install -r requirements.txt --upgrade
```

### Poor performance
```bash
# Profile to find bottlenecks
python3 scripts/profile_performance.py

# Check system resources
top -o cpu

# Reduce vision quality in config
# Edit config/test_agent.yaml:
# vision.detection_confidence: 0.5 (lower = faster)
```

---

## Next Steps

### 1. Run Full E2E Test
```bash
python3 scripts/test_e2e.py --actions 20
```

### 2. Review Documentation
- [API Documentation](docs/api/index.md)
- [E2E Testing Guide](E2E_TESTING_GUIDE.md)
- [Performance Report](PERFORMANCE_REPORT.md)

### 3. Start Training
```bash
# Run 10 training episodes
python3 -m src.orchestrator.cli train \
  --episodes 10 \
  --window "Cultist Simulator"
```

### 4. Monitor Progress
```bash
# View TensorBoard logs
tensorboard --logdir data/tensorboard

# Open browser to http://localhost:6006
```

### 5. Analyze Results
```bash
# Check session logs
ls data/sessions/

# View latest session
cat data/sessions/session_*.json | python3 -m json.tool
```

---

## Project Structure

```
cultist-simulator/
├── src/                    # Source code
│   ├── vision/            # Screen capture, detection, OCR
│   ├── automation/        # Input simulation
│   ├── safety/            # Constraint validation
│   ├── nlp/               # Text analysis
│   ├── learning/          # RL agent
│   ├── orchestrator/      # Main agent runner
│   └── lib/               # Shared utilities
├── tests/                 # Test suites
│   ├── contract/          # Interface tests
│   ├── unit/              # Component tests
│   ├── integration/       # Pipeline tests
│   └── performance/       # Benchmark tests
├── scripts/               # Utility scripts
│   ├── test_e2e.py       # E2E test runner
│   ├── find_window.py    # Window detector
│   └── profile_performance.py  # Profiling
├── config/                # Configuration files
├── data/                  # Data directory
│   ├── knowledge_base.db  # SQLite database
│   ├── sessions/          # Session logs
│   ├── logs/              # Application logs
│   └── tensorboard/       # Training metrics
└── docs/                  # Documentation
    └── api/               # API reference
```

---

## Development

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific suite
pytest tests/integration/

# Performance tests
pytest tests/performance/ -v
```

### Code Quality
```bash
# Type checking
mypy src/

# Linting
pylint src/

# Formatting
black src/ tests/
```

### Adding Features
1. Write tests first (TDD)
2. Implement feature
3. Update documentation
4. Run full test suite
5. Regenerate API docs: `python3 scripts/generate_docs.py`

---

## Support

### Documentation
- [API Reference](docs/api/index.md)
- [E2E Testing Guide](E2E_TESTING_GUIDE.md)
- [Performance Report](PERFORMANCE_REPORT.md)
- [Task Progress](TASK_PROGRESS_REPORT.md)

### Logs
- Application: `data/logs/agent_*.jsonl`
- Sessions: `data/sessions/`
- TensorBoard: `data/tensorboard/`

### Common Issues
- Check [E2E Testing Guide](E2E_TESTING_GUIDE.md) troubleshooting section
- Review test outputs for specific errors
- Enable verbose logging in config

---

## Quick Reference

```bash
# Setup
source venv/bin/activate
pytest  # Verify installation

# Find game window
python3 scripts/find_window.py

# Dry run test
python3 scripts/test_e2e.py --dry-run

# Live test
python3 scripts/test_e2e.py --actions 10

# Training
python3 -m src.orchestrator.cli train --episodes 50

# Performance check
python3 scripts/profile_performance.py

# View metrics
tensorboard --logdir data/tensorboard
```

---

**Ready to go!** 🚀

Start with the dry-run test, then proceed to live testing and training. The agent will learn and improve over time!
