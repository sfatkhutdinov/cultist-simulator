# Cultist Simulator AI Agent

An autonomous AI agent that learns to play and win Cultist Simulator through self-discovery and experimentation.

## Features

- **Computer Vision**: Real-time game state capture and element detection using YOLOv8 and OCR
- **Reinforcement Learning**: PPO-based agent that learns optimal strategies through trial and error
- **Natural Language Processing**: Semantic understanding of narrative text and goal extraction
- **Safe Automation**: macOS input simulation with 100% reliable safety containment
- **Knowledge Base**: Persistent SQLite storage of game mechanics and learned patterns
- **🛡️ Single-Screen Safe**: Strictly confined to game window with focus monitoring

## 🚨 Safety First

**Perfect for single-screen Mac setups!** The agent includes multiple safety layers:

✅ **Active Window Validation** - Only runs when game window is focused  
✅ **Strict Boundary Enforcement** - All clicks validated against window bounds  
✅ **Focus Monitoring** - Pauses immediately if window loses focus  
✅ **Emergency Stop** - Instant shutdown via Ctrl+C or F12  
✅ **Keyboard Blacklist** - Cmd+Q, Cmd+W, etc. are blocked  
✅ **Violation Logging** - Complete audit trail of all safety checks  

👉 **See [docs/SINGLE_SCREEN_SAFETY.md](docs/SINGLE_SCREEN_SAFETY.md) for details**

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup
python -m pytest tests/  # Verify installation

# IMPORTANT: Focus Cultist Simulator window, then:
python -m src.orchestrator.cli run --agent-id my_agent --window "Cultist Simulator"
```

**First time setup:**
1. Grant macOS permissions (Screen Recording + Accessibility)
2. Open Cultist Simulator
3. Click on game window to make it active
4. Run agent command (agent will verify window is focused)

## Project Structure

See `specs/001-autonomous-ai-agent/plan.md` for complete architecture documentation.

## Development

This project follows Test-Driven Development (TDD). All tests must be written and failing before implementation.

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
pylint src/
```

## License

MIT
