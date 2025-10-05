#!/bin/bash
# Quick Start Training Script
# Launches training with verbose logging and TensorBoard in Safari

cd "$(dirname "$0")"

echo "🚀 Starting Cultist Simulator AI Training"
echo "========================================"
echo ""
echo "This will:"
echo "  1. Enable verbose logging (DEBUG level)"
echo "  2. Launch TensorBoard automatically"
echo "  3. Open TensorBoard in Safari"
echo "  4. Train for 50 episodes"
echo ""
echo "Press Ctrl+C to stop training at any time."
echo ""

# Run training
python -m src.orchestrator.cli train \
  --agent-id my_agent \
  --episodes 50 \
  --window "Cultist Simulator" \
  --verbose

echo ""
echo "✓ Training complete!"
