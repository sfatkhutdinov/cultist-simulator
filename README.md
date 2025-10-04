# Cultist Simulator AI Agent

An autonomous AI agent that learns to play and win Cultist Simulator through self-discovery and experimentation.

## Features

- **Computer Vision**: Real-time game state capture and element detection using YOLOv8 and OCR
- **Reinforcement Learning**: PPO-based agent that learns optimal strategies through trial and error
- **Natural Language Processing**: Semantic understanding of narrative text and goal extraction
- **Safe Automation**: macOS input simulation with 100% reliable safety containment
- **Knowledge Base**: Persistent SQLite storage of game mechanics and learned patterns

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup
python -m pytest tests/  # Verify installation

# Start training
python -m src.orchestrator.cli --run-episode
```

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
