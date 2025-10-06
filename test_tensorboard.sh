#!/bin/bash
# Test TensorBoard Integration
# Runs 2 episodes to verify TensorBoard logging works

cd "$(dirname "$0")"

echo "🧪 Testing TensorBoard Integration"
echo "===================================="
echo ""
echo "Running 2 test episodes to verify TensorBoard is working..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run minimal training
python3 -m src.orchestrator.cli train \
  --agent-id tensorboard_test \
  --episodes 2 \
  --max-actions 5 \
  --checkpoint 1 \
  --window "Cultist Simulator" \
  --verbose

echo ""
echo "===================================="
echo "✅ Test complete!"
echo ""
echo "Checking TensorBoard data..."
ls -lh data/tensorboard/

echo ""
echo "If you see event files above, TensorBoard is working!"
echo ""
echo "Launch TensorBoard with:"
echo "  tensorboard --logdir data/tensorboard"
echo ""
