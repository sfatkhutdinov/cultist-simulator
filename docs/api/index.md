# API Documentation Index

**Cultist Simulator AI Agent**  
**Generated**: 2025-10-04 22:36:32

This documentation covers all public APIs for the autonomous AI agent system.

---

## Libraries

### [Vision](vision.md)

Vision Library - Screen capture and element detection for Cultist Simulator.

### [Automation](automation.md)

Automation Library - Safe macOS Input Simulation

### [Safety](safety.md)

Safety Library - Critical safety validation for agent actions.

### [Nlp](nlp.md)

NLP Library - Natural Language Processing for Cultist Simulator AI Agent.

### [Learning](learning.md)

Learning Library - RL Agent and Knowledge Management

### [Lib.Types](lib_types.md)

Shared type definitions for Cultist Simulator AI Agent.


---

## Quick Links

- [Vision Library](vision.md) - Screen capture, element detection, OCR
- [Automation Library](automation.md) - Safe input simulation
- [Safety Library](safety.md) - Constraint validation
- [NLP Library](nlp.md) - Narrative text analysis
- [Learning Library](learning.md) - RL agent and knowledge base
- [Type Definitions](lib_types.md) - Shared data structures

---

## Getting Started

Import libraries:

```python
from src.vision import capture_game_state, detect_elements
from src.automation import simulate_click, simulate_key_press
from src.safety import validate_action
from src.nlp import analyze_text, extract_goals
from src.learning import select_action, update_knowledge
```

## Example Usage

```python
# Capture game state
game_state = capture_game_state("Cultist Simulator")

# Select action
action = select_action(game_state)

# Validate with safety
validation = validate_action(action, context)

if validation.is_allowed:
    # Execute action
    result = simulate_click(action.point, "left", window_bounds)
```

---

## Architecture

The system consists of 5 main libraries:

1. **Vision** - Captures and analyzes game state
2. **Automation** - Executes actions safely
3. **Safety** - Validates all actions
4. **NLP** - Understands narrative text
5. **Learning** - Makes decisions and learns

All libraries use shared type definitions from `src.lib.types`.

---

## Testing

Run tests:
```bash
pytest tests/
```

All libraries have:
- Contract tests (interface validation)
- Unit tests (component testing)
- Integration tests (pipeline testing)
- Performance tests (NFR validation)

---

## Contributing

When adding new functions:
1. Add comprehensive docstrings
2. Include type hints
3. Write tests first (TDD)
4. Regenerate docs: `python3 scripts/generate_docs.py`

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
