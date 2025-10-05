# 🚀 THE COMMAND YOU ASKED FOR

## To start training with verbose logging and TensorBoard in Safari:

```bash
python -m src.orchestrator.cli train --agent-id my_agent --episodes 50 --window "Cultist Simulator" --verbose
```

Or shorter:
```bash
python -m src.orchestrator.cli train --agent-id my_agent --episodes 50 -v
```

Or use the convenience script:
```bash
./start_training.sh
```

---

## What Will Happen:

1. ✅ **Verbose logging enabled** - You'll see DEBUG level logs in terminal
2. ✅ **TensorBoard starts** - Launches automatically on port 6006
3. ✅ **Safari opens** - Automatically opens to http://localhost:6006
4. ✅ **Training begins** - Agent starts learning
5. ✅ **Auto cleanup** - TensorBoard stops when done or interrupted

---

## If TensorBoard Fails:

Training will **immediately abort** with an error message, so you can fix it before wasting time training without monitoring.

---

## To Stop Training:

Press **Ctrl+C** - TensorBoard will automatically clean up.

---

**That's it! Just run the command above and Safari will open with TensorBoard automatically.**
