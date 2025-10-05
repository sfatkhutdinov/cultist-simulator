# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an autonomous AI agent that learns to play Cultist Simulator through reinforcement learning, computer vision, and natural language processing. The agent uses multiple safety layers to ensure safe operation on macOS.

## Common Development Commands

### Testing
```bash
# Run all tests (expected: 146 passed, 14 skipped)
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=xml

# Run specific test categories
pytest tests/unit/           # Unit tests
pytest tests/contract/       # Interface tests
pytest tests/integration/    # Integration tests
pytest tests/performance/    # Performance benchmarks

# Run single test file
pytest tests/unit/test_vision.py -v
```

### Code Quality
```bash
# Type checking
mypy src/

# Code formatting
black src/ tests/

# Linting
pylint src/
```

### Database Setup
```bash
# Initialize SQLite knowledge base
python3 scripts/init_database.py
```

### Development Testing
```bash
# Find game window (run Cultist Simulator first)
python3 scripts/find_window.py

# Dry run test (safe - no actual clicks)
python3 scripts/test_e2e.py --dry-run --actions 5

# Live end-to-end test
python3 scripts/test_e2e.py --actions 10

# Performance profiling
python3 scripts/profile_performance.py
```

### Running the Agent
```bash
# Single episode
python3 -m src.orchestrator.cli run --agent-id my_agent --window "Cultist Simulator"

# Training mode
python3 -m src.orchestrator.cli train --episodes 10 --window "Cultist Simulator"

# View TensorBoard metrics
tensorboard --logdir data/tensorboard
```

## Architecture Overview

The codebase follows a modular architecture with clear separation of concerns:

### Core Libraries (src/)
- **vision/**: Screen capture, YOLOv8 object detection, EasyOCR text extraction
- **automation/**: macOS input simulation using pyobjc frameworks
- **safety/**: Action validation with strict boundary checking and focus monitoring
- **nlp/**: Narrative text analysis using sentence transformers
- **learning/**: PPO reinforcement learning agent with SQLite knowledge base
- **orchestrator/**: Main coordination layer that implements perception-decision-action loop
- **lib/**: Shared utilities including logging, configuration, and type definitions

### Key Design Patterns

**Safety-First Architecture**: All actions flow through safety validation before execution. The safety module has 100% veto power over any action.

**Plugin-Based CLI**: Each major component (`vision`, `automation`, `safety`, `nlp`, `learning`) has its own CLI interface accessible via `python3 -m src.<component>.cli`.

**Knowledge Persistence**: Game mechanics and learned strategies are stored in SQLite (`data/knowledge_base.db`) for persistent learning across sessions.

**Event-Driven Coordination**: The orchestrator coordinates all libraries through a perception-decision-action loop, with each step clearly separated and testable.

## Development Workflow

This project follows **Test-Driven Development (TDD)**:
1. Write failing tests first
2. Implement minimal code to pass
3. Refactor while keeping tests green
4. All new features require tests

### Test Categories
- **Unit tests** (`tests/unit/`): Individual component testing
- **Contract tests** (`tests/contract/`): Library interface validation
- **Integration tests** (`tests/integration/`): Cross-library functionality
- **Performance tests** (`tests/performance/`): Benchmark validation

## Safety and Constraints

The agent is designed for safe operation on single-screen macOS setups:

- **Window Focus Validation**: Only operates when game window is focused
- **Boundary Enforcement**: All clicks validated against window bounds
- **Emergency Stop**: F12 or Ctrl+C for immediate shutdown
- **Keyboard Blacklist**: System shortcuts (Cmd+Q, Cmd+W) are blocked
- **Rate Limiting**: Maximum 2 actions per second

## Configuration

Main config files:
- `config/test_agent.yaml`: Agent behavior and safety settings
- `pyproject.toml`: Testing, linting, and dependency configuration
- `requirements.txt`: Python package dependencies

## Data Storage

- `data/knowledge_base.db`: SQLite database with game mechanics and strategies
- `data/sessions/`: JSON logs of agent sessions
- `data/tensorboard/`: Training metrics for visualization
- `data/logs/`: Application logs in structured format

## Dependencies

Key dependencies include:
- **ML/RL**: torch, stable-baselines3, gymnasium
- **Vision**: opencv-python, ultralytics (YOLOv8), easyocr
- **NLP**: sentence-transformers, transformers
- **macOS**: pyobjc-framework-Quartz, pyobjc-framework-ApplicationServices
- **Testing**: pytest, pytest-cov
- **Quality**: black, mypy, pylint

## Troubleshooting

### Permission Issues
Grant macOS permissions for Screen Recording and Accessibility in System Settings → Privacy & Security.

### Window Detection
Use `python3 scripts/find_window.py` to verify game window detection.

### Test Failures
Run `pytest -v` for detailed output. Check the warnings guide in `WARNINGS_GUIDE.md` for known issues.

### Performance Issues
Use `python3 scripts/profile_performance.py` to identify bottlenecks.