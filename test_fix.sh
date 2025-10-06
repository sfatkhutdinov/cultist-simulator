#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

echo "Testing critical fixes..."
echo "1. Window bounds verification"
echo "2. TensorBoard logging"
echo "3. Emergency stop (Cmd+Shift+Q)"
echo ""
echo "Running 1 episode with 3 actions..."
echo ""

python3 -m src.orchestrator.cli train \
  --agent-id fix_test \
  --episodes 1 \
  --max-actions 3 \
  --checkpoint 1 \
  --window "Cultist Simulator" \
  --verbose

echo ""
echo "Checking results..."
ls -lh data/tensorboard/
echo ""
echo "Test complete. Press Ctrl+C or Cmd+Shift+Q worked to stop?"
