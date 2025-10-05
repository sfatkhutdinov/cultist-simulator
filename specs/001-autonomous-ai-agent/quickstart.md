# Quickstart Guide: Autonomous AI Agent Development

**Feature**: Autonomous AI Agent for Cultist Simulator  
**Date**: 2025-10-04  
**Audience**: Developers implementing this feature

---

## Prerequisites

### System Requirements
- **macOS**: 13.0+ (Ventura or later)
- **Python**: 3.11+
- **Game**: Cultist Simulator (installed and runnable)
- **RAM**: 8GB minimum (16GB recommended for model training)
- **GPU**: Optional but recommended for faster vision/NLP processing

### macOS Permissions

The agent requires special permissions to control the game:

1. **Accessibility**: System Settings → Privacy & Security → Accessibility → Add Terminal/IDE
2. **Screen Recording**: System Settings → Privacy & Security → Screen Recording → Add Terminal/IDE

Without these, the automation library cannot function.

---

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd cultist-simulator
git checkout 001-autonomous-ai-agent
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies
```bash
# Install all libraries
pip install -r requirements.txt

# Download YOLO weights (one-time)
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Download NLP model (one-time)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Download EasyOCR models (one-time)
python -c "import easyocr; reader = easyocr.Reader(['en'])"
```

### 4. Initialize Database
```bash
python -m scripts.init_database
# Creates data/knowledge_base.db with schema
```

---

## Project Structure

```
cultist-simulator/
├── src/                      # Source code
│   ├── vision/               # Computer vision library
│   ├── automation/           # Input simulation library
│   ├── learning/             # RL agent library
│   ├── nlp/                  # Text analysis library
│   ├── safety/               # Safety constraints library
│   ├── orchestrator/         # Main agent runner
│   └── lib/                  # Shared utilities
├── tests/                    # Test suite
│   ├── contract/             # Library contract tests
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
├── data/                     # Runtime data
│   ├── knowledge_base.db     # SQLite database
│   ├── sessions/             # Session recordings
│   ├── models/               # Model checkpoints
│   └── logs/                 # Log files
├── specs/                    # Specification documents
└── requirements.txt          # Python dependencies
```

---

## Development Workflow (TDD)

**Constitution Principle III**: Test-First Development is MANDATORY.

### Step 1: Write Tests First
```bash
# Example: Adding a new vision function
cd tests/contract
# Create test_vision_new_feature.py

# Write failing tests
pytest tests/contract/test_vision_new_feature.py
# Tests should FAIL (red)
```

### Step 2: Get User Approval
- Show test file to stakeholder/user
- Confirm tests match requirements
- Only proceed after approval

### Step 3: Implement to Pass Tests
```bash
# Implement feature in src/vision/
# Run tests until they pass (green)
pytest tests/contract/test_vision_new_feature.py
```

### Step 4: Refactor
```bash
# Clean up code while keeping tests green
# Run full test suite
pytest tests/
```

---

## Running the Agent

### Initial Setup

1. **Start Cultist Simulator**:
   ```bash
   # Launch the game manually
   # Create a new game or load a saved game
   # Leave it at the starting screen
   ```

2. **Configure Agent**:
   ```bash
   # Edit config/agent_config.yaml
   window_name: "Cultist Simulator"
   training_episodes: 100
   checkpoint_interval: 10
   ```

3. **Run Agent**:
   ```bash
   # Start training
   python -m src.orchestrator.cli --train --episodes 100
   
   # Or run single episode with debug output
   python -m src.orchestrator.cli --run-episode --debug
   ```

### Monitoring Progress

```bash
# Watch logs in real-time
tail -f data/logs/agent.log

# View metrics dashboard (TensorBoard)
tensorboard --logdir=data/logs/tensorboard

# Query knowledge base
python -m src.learning.cli --query-knowledge --type mechanics

# Check current metrics
python -m src.learning.cli --metrics --last-n 50
```

---

## Testing

### Run All Tests
```bash
# Full test suite
pytest tests/

# With coverage report
pytest tests/ --cov=src --cov-report=html

# View coverage
open htmlcov/index.html
```

### Run Specific Test Suites
```bash
# Contract tests only
pytest tests/contract/

# Integration tests (requires game running)
pytest tests/integration/

# Unit tests only
pytest tests/unit/

# Specific library tests
pytest tests/contract/test_vision_contract.py -v
```

### Safety Tests (Critical)
```bash
# Run adversarial safety tests
pytest tests/contract/test_safety_contract.py::test_adversarial_attacks -v

# This MUST pass with 100% success
```

---

## CLI Commands Reference

### Vision Library
```bash
# Capture current game state
python -m src.vision.cli --capture-game-state --output state.json

# Benchmark vision performance
python -m src.vision.cli --benchmark --iterations 100
```

### Automation Library
```bash
# Test click (with safety bounds)
python -m src.automation.cli --click 500 300 --window-bounds "0,0,1920,1080"

# Get blacklisted keys
python -m src.automation.cli --blacklist
```

### Learning Library
```bash
# Train agent for N episodes
python -m src.learning.cli --train --episodes 100

# Query knowledge base
python -m src.learning.cli --query-knowledge --type similar_states --params '{"state_hash":"abc"}'

# View current strategy
python -m src.learning.cli --articulate-strategy
```

### NLP Library
```bash
# Analyze narrative text
python -m src.nlp.cli --analyze-text "You have discovered forbidden knowledge"

# Find similar narratives
python -m src.nlp.cli --find-similar "ancient ritual" --top-k 5
```

### Safety Library
```bash
# Validate an action
python -m src.safety.cli --validate-action action.json --context context.json

# Run safety test suite
python -m src.safety.cli --test-constraints --adversarial
```

---

## Debugging

### Enable Debug Mode
```bash
# Run with verbose logging
python -m src.orchestrator.cli --run-episode --debug --log-level DEBUG

# This shows:
# - Vision processing pipeline
# - Action selection reasoning
# - Safety validation details
# - Performance timings
```

### Common Issues

1. **"WindowNotFoundError"**:
   - Game not running
   - Window name mismatch in config
   - Solution: Check game is running, verify window name

2. **"Permission Denied" for automation**:
   - Missing Accessibility permissions
   - Solution: Grant permissions in System Settings

3. **"Model too slow"**:
   - CPU-only inference
   - Solution: Enable GPU in config, reduce image resolution

4. **"Loop detection false positives"**:
   - Sensitivity too high
   - Solution: Adjust `loop_similarity_threshold` in config

---

## Performance Optimization

### GPU Acceleration
```python
# In config/agent_config.yaml
vision:
  yolo_device: "mps"  # Use Apple Silicon GPU
  ocr_gpu: true

nlp:
  device: "mps"
```

### Reduce Latency
- Lower capture resolution (vision_config.capture_resolution)
- Reduce YOLO confidence threshold (fewer detections)
- Cache element templates more aggressively
- Disable debug logging in production

---

## Data Management

### Session Recordings
```bash
# List all sessions
ls data/sessions/

# Replay a session
python -m src.orchestrator.cli --replay-session <session_id>

# Export session to JSON
python -m src.learning.cli --export-session <session_id> --output session.json
```

### Knowledge Base
```bash
# Backup database
cp data/knowledge_base.db data/backups/kb_$(date +%Y%m%d).db

# Export knowledge to JSON
python -m src.learning.cli --export-knowledge --output knowledge.json

# Import knowledge
python -m src.learning.cli --import-knowledge knowledge.json
```

---

## Safety Checklist

Before deploying the agent, verify:

- [ ] Accessibility permissions granted
- [ ] Screen Recording permissions granted
- [ ] All safety tests passing (100% success rate)
- [ ] Game window bounds correctly detected
- [ ] Emergency stop key (F12) functional
- [ ] Rate limiting active
- [ ] Key blacklist includes all dangerous combinations
- [ ] Focus check enabled

**Critical**: Never disable safety validation in production.

---

## Next Steps

### Quick Test Run

After setup, test the agent with a minimal run:

```bash
# Activate environment
source venv/bin/activate

# Launch Cultist Simulator game first
# Make sure the game window is visible

# Run agent for 1 episode (test mode)
python -m src.orchestrator.cli --episodes 1 --config config/test_agent.yaml

# Monitor TensorBoard (in separate terminal)
tensorboard --logdir data/tensorboard/
```

### Full Training Run

Once testing is successful:

```bash
# Run full training (100 episodes with aggressive exploration)
python -m src.orchestrator.cli --episodes 100 --config config/aggressive.yaml

# Or run conservative approach  
python -m src.orchestrator.cli --episodes 100 --config config/conservative.yaml

# View real-time progress
# Open browser to http://localhost:6006 for TensorBoard
```

### Verify Installation

```bash
# Run library smoke tests
python -m src.vision.cli analyze --help
python -m src.automation.cli --help  
python -m src.safety.cli --help
python -m src.nlp.cli --help
python -m src.learning.cli --help

# Run test suite
pytest tests/contract/ -v
pytest tests/integration/ -v
pytest tests/unit/ -v
```

---

## Training Phases

1. **Phase 1**: Run initial training (10-20 episodes)
   - Goal: Verify agent executes without crashes
   - Expected: Agent completes sessions, saves knowledge
   - Duration: ~1-2 hours

2. **Phase 2**: Analyze results, tune hyperparameters
   - Review TensorBoard metrics
   - Adjust exploration rate, learning rate
   - Iterate on reward function

3. **Phase 3**: Scale up training (100-500 episodes target)
   - Goal: Achieve first win (FR-026 requirement)
   - Expected: Win within 100-500 attempts
   - Duration: ~24-48 hours (depends on game complexity)

4. **Phase 4**: Evaluate multi-dimensional metrics
   - Track survival time, win rate, resources, unique endings
   - Verify >80% narrative understanding accuracy (FR-022)
   - Validate performance <1000ms action selection (NFR-001)

5. **Phase 5**: Iterate on reward function and strategy
   - Refine based on observed patterns
   - Implement strategy evolution
   - Achieve consistent wins

---

## Getting Help

- **Logs**: Check `data/logs/agent.log` for errors
- **Tests**: Run test suite to verify setup
- **Metrics**: View TensorBoard for training progress
- **Documentation**: See `specs/001-autonomous-ai-agent/` for detailed docs

---

## Constitutional Compliance

This feature follows all constitution principles:

- ✅ **Library-First**: Each component is an independent library
- ✅ **CLI Interface**: Every library exposes CLI with JSON I/O
- ✅ **Test-First**: TDD workflow mandatory
- ✅ **Integration Testing**: Cross-library tests included
- ✅ **Observability**: Structured logging throughout

See `plan.md` for full constitutional compliance documentation.
