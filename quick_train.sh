#!/bin/bash
# Quick Training Data Collection Script
# Runs a short 5-episode training session to collect initial data

cd "$(dirname "$0")"

echo "🚀 CULTIST SIMULATOR AI - QUICK TRAINING SESSION"
echo "================================================"
echo ""
echo "This will run 5 short episodes to collect training data."
echo "Press Cmd+Shift+Q or Ctrl+C to stop at any time."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run quick training session
python3 -m src.orchestrator.cli train \
  --agent-id "data_collection_$(date +%Y%m%d_%H%M%S)" \
  --episodes 5 \
  --max-actions 10 \
  --checkpoint 2 \
  --window "Cultist Simulator" \
  --verbose

echo ""
echo "================================================"
echo "✅ Training session complete!"
echo ""
echo "📊 Check your data:"
echo "  - Checkpoints: ls -lah data/checkpoints/"
echo "  - TensorBoard: tensorboard --logdir data/tensorboard"
echo "  - Database: sqlite3 data/knowledge_base.db"
echo ""
