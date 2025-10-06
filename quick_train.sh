#!/bin/bash
# Quick Test Training Script
# Fast verification that training system works

cd "$(dirname "$0")"

echo "⚡ QUICK TRAINING TEST"
echo "====================="
echo ""
echo "Configuration:"
echo "  Episodes:     5"
echo "  Max Actions:  20 per episode"
echo "  Checkpoints:  Every 2 episodes"
echo ""
echo "This quick test verifies:"
echo "  ✓ Window detection working"
echo "  ✓ Vision system operational"
echo "  ✓ Action execution safe"
echo "  ✓ Data collection active"
echo "  ✓ TensorBoard logging"
echo ""
echo "Duration: ~2-3 minutes"
echo ""

# Activate virtual environment
source venv/bin/activate

# Start TensorBoard
echo "📊 Starting TensorBoard..."
pkill -f tensorboard 2>/dev/null
tensorboard --logdir data/tensorboard --host localhost --port 6006 > /dev/null 2>&1 &
sleep 2
echo "✓ TensorBoard: http://localhost:6006"
echo ""

# Run quick test (--no-tensorboard since we already started it)
python3 -m src.orchestrator.cli train \
  --agent-id "quick_test_$(date +%Y%m%d_%H%M%S)" \
  --episodes 5 \
  --max-actions 20 \
  --checkpoint 2 \
  --window "Cultist Simulator" \
  --no-tensorboard \
  --verbose

echo ""
echo "====================="
echo "✅ Test Complete!"
echo ""
echo "Check TensorBoard for metrics: http://localhost:6006"
echo ""
