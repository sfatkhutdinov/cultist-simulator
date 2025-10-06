#!/bin/bash
# Production Training Script
# Runs extended training session with optimal parameters

cd "$(dirname "$0")"

echo "🚀 CULTIST SIMULATOR AI - PRODUCTION TRAINING"
echo "=============================================="
echo ""
echo "Training Configuration:"
echo "  Episodes:        200"
echo "  Max Actions:     150 per episode"
echo "  Checkpoints:     Every 20 episodes"
echo "  Emergency Stop:  Cmd+Shift+Q"
echo ""
echo "This will collect extensive training data for:"
echo "  ✓ Reinforcement Learning model"
echo "  ✓ Game state understanding"
echo "  ✓ Action pattern recognition"
echo "  ✓ UI element detection (via color/OCR)"
echo ""
echo "Estimated duration: 1-2 hours"
echo ""
echo "Monitor progress: http://localhost:6006"
echo ""
read -p "Press Enter to start training (Ctrl+C to cancel)..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Start TensorBoard in background
echo "📊 Starting TensorBoard..."
pkill -f tensorboard 2>/dev/null
tensorboard --logdir data/tensorboard --host localhost --port 6006 > /dev/null 2>&1 &
sleep 2
echo "✓ TensorBoard running at http://localhost:6006"
echo ""

# Run production training (--no-tensorboard since we already started it)
python3 -m src.orchestrator.cli train \
  --agent-id "production_$(date +%Y%m%d_%H%M%S)" \
  --episodes 200 \
  --max-actions 150 \
  --checkpoint 20 \
  --window "Cultist Simulator" \
  --no-tensorboard \
  --verbose

echo ""
echo "=============================================="
echo "✅ Training Complete!"
echo ""
echo "📊 View Results:"
echo "  TensorBoard: http://localhost:6006"
echo "  Checkpoints: ls -lh data/checkpoints/"
echo "  Logs:        ls -lh data/logs/"
echo ""
echo "📈 Next Steps:"
echo "  1. Analyze TensorBoard metrics"
echo "  2. Review action patterns in logs"
echo "  3. Train YOLO on collected screenshots (future)"
echo "  4. Train RL model on collected experiences"
echo ""
