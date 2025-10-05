# Training Command Reference

## Quick Start - Training with Verbose Logging and TensorBoard in Safari

### Recommended Command

```bash
python -m src.orchestrator.cli train --agent-id my_agent --episodes 50 --window "Cultist Simulator" --verbose
```

This command will:
1. ✅ Start training with **verbose logging** (DEBUG level)
2. ✅ Automatically launch **TensorBoard**
3. ✅ Open TensorBoard in **Safari** at http://localhost:6006
4. ✅ Handle cleanup when training completes or is interrupted

---

## Command Options

### Basic Training (No Verbose, No TensorBoard)
```bash
python -m src.orchestrator.cli train --agent-id my_agent --episodes 50 --no-tensorboard
```

### Training with Verbose Logging Only
```bash
python -m src.orchestrator.cli train --agent-id my_agent --episodes 50 --verbose --no-tensorboard
```

### Training with TensorBoard Only (No Verbose)
```bash
python -m src.orchestrator.cli train --agent-id my_agent --episodes 50
```

### Full Features (Verbose + TensorBoard in Safari)
```bash
python -m src.orchestrator.cli train --agent-id my_agent --episodes 50 --verbose
```
Or use the short flag:
```bash
python -m src.orchestrator.cli train --agent-id my_agent --episodes 50 -v
```

---

## All Available Flags

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--agent-id` | - | Agent identifier | `agent_001` |
| `--episodes` | `-n` | Number of training episodes | `100` |
| `--window` | - | Game window name | `Cultist Simulator` |
| `--max-actions` | - | Max actions per episode | `1000` |
| `--max-duration` | - | Max episode duration (seconds) | `300.0` |
| `--checkpoint` | - | Save checkpoint every N episodes | `10` |
| `--verbose` | `-v` | Enable DEBUG level logging | `False` |
| `--no-tensorboard` | - | Disable auto TensorBoard launch | `False` |

---

## What Happens During Training

### 1. Initialization
```
🔍 Verbose logging enabled (DEBUG level)
Training agent: my_agent
Episodes: 50
Window: Cultist Simulator
Max actions per episode: 1000
OCR enabled: True
Checkpoint every 10 episodes
```

### 2. TensorBoard Launch
```
📊 Starting TensorBoard...
⏳ Waiting for TensorBoard to initialize...
✓ TensorBoard started successfully
🌐 Opening TensorBoard in Safari...
✓ Safari opened with TensorBoard at http://localhost:6006
```

### 3. Training Progress
The agent will run episodes and log progress. With `--verbose`, you'll see detailed DEBUG logs.

### 4. Completion
```
============================================================
Training Complete!
============================================================
Episodes: 50
Total Actions: 1250
Average Actions per Episode: 25.0
============================================================

Final Metrics:
  total_episodes: 50
  success_rate: 0.82
  average_reward: 125.50
```

### 5. Cleanup
```
🛑 Stopping TensorBoard...
✓ TensorBoard stopped
```

---

## Error Handling

### TensorBoard Fails to Start
If TensorBoard fails to launch, training will **abort immediately**:

```
❌ Failed to start TensorBoard: TensorBoard not found. Install with: pip install tensorboard
Training aborted.
```

**Solution**: Install TensorBoard:
```bash
pip install tensorboard
```

### Safari Fails to Open
If Safari fails to open, training will abort:

```
❌ Failed to start TensorBoard: Failed to open Safari: [error details]
Training aborted.
```

**Solutions**:
- Make sure Safari is installed
- Or use `--no-tensorboard` and manually open http://localhost:6006

### Training Interrupted (Ctrl+C)
```
Training interrupted by user.
🛑 Stopping TensorBoard...
✓ TensorBoard stopped
```

TensorBoard is automatically cleaned up.

---

## Viewing TensorBoard

Once Safari opens, you'll see:
- **Scalars**: Episode rewards, success rates, loss curves
- **Distributions**: Action distributions, value estimates
- **Graphs**: Neural network architecture
- **Time Series**: Real-time training metrics

Navigate the tabs in TensorBoard to explore different visualizations.

---

## Advanced Usage

### Custom Configuration
Edit `config/test_agent.yaml` to customize:
- Vision settings (OCR, YOLO, etc.)
- Learning parameters
- Safety constraints

### Multiple Training Sessions
Run multiple agents in parallel (in different terminals):

**Terminal 1:**
```bash
python -m src.orchestrator.cli train --agent-id agent_alpha --episodes 50 -v
```

**Terminal 2:**
```bash
python -m src.orchestrator.cli train --agent-id agent_beta --episodes 50 -v --no-tensorboard
```

Then manually launch TensorBoard to view both:
```bash
tensorboard --logdir data/tensorboard
```

### Resuming Training
The agent automatically saves checkpoints. To resume:
```bash
python -m src.orchestrator.cli train --agent-id my_agent --episodes 100 -v
```

It will load the previous checkpoint and continue.

---

## Troubleshooting

### Port 6006 Already in Use
If you get an error about port 6006:

1. Kill existing TensorBoard:
```bash
pkill -f tensorboard
```

2. Or manually check and kill:
```bash
lsof -ti:6006 | xargs kill -9
```

### Logs Not Showing in TensorBoard
- Make sure training is actually running
- Refresh Safari (Cmd+R)
- Check that `data/tensorboard/` contains log files
- Wait a few seconds for TensorBoard to sync

### Verbose Logs Too Much
If verbose logging is overwhelming:
- Remove `--verbose` flag
- Logs will still be saved to `data/logs/` in JSON format
- Review them later with: `cat data/logs/agent_*.jsonl | jq`

---

## Example Session

```bash
# Terminal 1: Start training with verbose logging and TensorBoard
cd /Users/stan/Documents/Programming/cultist-simulator
python -m src.orchestrator.cli train \
  --agent-id my_first_agent \
  --episodes 50 \
  --window "Cultist Simulator" \
  --max-actions 500 \
  --checkpoint 10 \
  --verbose

# Safari will automatically open with TensorBoard
# Watch the metrics update in real-time as training progresses
# Training will auto-cleanup TensorBoard when done
```

---

## Files Generated

After training, you'll find:

- `data/tensorboard/` - TensorBoard logs
- `data/logs/agent_*.jsonl` - Structured JSON logs
- `data/sessions/` - Session replays
- `data/knowledge_base.db` - Learned game mechanics
- `models/` - Saved model checkpoints

---

## Next Steps

After training:

1. **View Metrics**: `python -m src.orchestrator.cli metrics --agent-id my_agent`
2. **View Strategy**: `python -m src.orchestrator.cli strategy --agent-id my_agent`
3. **Run Single Episode**: `python -m src.orchestrator.cli run --agent-id my_agent`
4. **Analyze Logs**: Check `data/logs/` for detailed session data

---

**Need Help?** See [QUICKSTART.md](QUICKSTART.md) for more information.
