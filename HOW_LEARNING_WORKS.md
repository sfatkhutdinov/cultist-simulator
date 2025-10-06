# How the AI Agent Learns Cultist Simulator (Without Knowing the Rules)

## 🎯 The Challenge

Cultist Simulator is notoriously complex:
- **Hidden mechanics**: No tutorial, rules discovered through play
- **Card combinations**: Hundreds of cards with emergent interactions
- **Time pressure**: Real-time card decay and verb timers
- **Failure states**: Multiple ways to lose (starvation, madness, imprisonment)
- **Victory conditions**: Multiple complex win conditions

**Question**: How can an AI learn this without being programmed with the rules?

**Answer**: **Reinforcement Learning** - the same approach that taught AlphaGo to beat world champions and taught robots to walk.

---

## 🧠 Reinforcement Learning in 3 Steps

### 1. **Experience the World**
The agent doesn't start with knowledge. It starts by **exploring**:
```
Episode 1: Random clicking → Dies in 3 minutes
Episode 2: Tries dragging cards → Discovers verbs work
Episode 50: Patterns emerge → Understands basic card flows
Episode 200: Strategic play → Discovers winning combinations
```

### 2. **Observe the Consequences**
After each action, the agent asks: "What changed?"
```python
State Before:  [Screen with 5 cards, Health=5, Time=10s]
Action:        DRAG card "Work" to verb "Work"
State After:   [Screen with 6 cards, Health=5, Time=8s, Funds+1]
Reward:        +1 (new card appeared, funds increased)
```

### 3. **Learn from Patterns**
Over hundreds of episodes, the agent discovers:
- "Dragging 'Work' to 'Work' verb → Usually gives Funds"
- "Ignoring Health cards → Game ends quickly (bad)"
- "Combining specific cards → Unlocks new opportunities (good)"
- "Certain sequences → Lead to victory (great!)"

---

## 🔬 How Our System Works

### **Phase 1: Random Exploration (Current)**
Right now, the agent is in **data collection mode**:

```
┌─────────────────────────────────────────────┐
│  EPISODE 1 (Random Actions)                 │
├─────────────────────────────────────────────┤
│  1. Capture screen                          │
│  2. Extract text with OCR                   │
│  3. Detect UI elements (colors)             │
│  4. Generate random action (click/drag/key) │
│  5. Verify action is safe (within window)   │
│  6. Execute action                          │
│  7. Log everything to database              │
│  8. Repeat 50-150 times                     │
└─────────────────────────────────────────────┘
         ↓
  DATA COLLECTED:
  ✓ Screenshots of game states
  ✓ Text extracted from UI
  ✓ Actions taken + results
  ✓ Temporal sequences
```

**What it's learning**:
- Where UI elements typically appear
- What text patterns exist in the game
- What actions are physically possible
- Rough correlation between actions and outcomes

### **Phase 2: Pattern Recognition (Next)**
After 200-500 episodes, we'll train **YOLO object detector**:

```
Training Data:
  → 10,000+ screenshots with UI elements

YOLO Model Output:
  "Card at (100, 200) - type: Health"
  "Verb at (500, 400) - type: Work"
  "Card at (300, 350) - type: Funds"
```

**What it learns**:
- Recognize specific card types visually
- Detect verb slots and their states
- Identify UI patterns (buttons, timers, warnings)

### **Phase 3: Strategic Learning (Final)**
Train **RL model** (PPO algorithm) on collected experiences:

```
Input (State):
  - Cards visible (from YOLO)
  - Text extracted (from OCR)
  - Time remaining
  - Recent action history

Output (Action):
  - Click position (x, y)
  - OR Drag from (x1, y1) to (x2, y2)
  - OR Press key (Space, Tab, etc.)

Reward Signal:
  +10  New card appeared
  +5   Verb completed successfully
  +1   Game still running
  -5   Warning message appeared
  -20  Health/Reason low
  -100 Game over (lost)
  +500 Victory!
```

**What it learns**:
- **Policy**: "In state X, action Y leads to good outcomes"
- **Value**: "This game state is worth Z points (how close to winning)"
- **Strategy**: "Prioritize Health when low, pursue victory when stable"

---

## 📊 The Learning Curve

### Episodes 1-50: **Blind Exploration**
```
Performance: Random (0% win rate)
Discovery: 
  ✓ Learned screen layout
  ✓ Found clickable regions
  ✓ Discovered card dragging works
  ✓ Identified verb slots
```

### Episodes 50-200: **Pattern Emergence**
```
Performance: Improving (0-5% win rate)
Discovery:
  ✓ Work verb → Funds cards
  ✓ Ignoring Health → Death
  ✓ Some cards create chains
  ✓ Time management matters
```

### Episodes 200-500: **Strategic Play**
```
Performance: Competent (10-30% win rate)
Discovery:
  ✓ Optimal card combinations
  ✓ Resource management strategies
  ✓ Victory path recognition
  ✓ Risk vs reward tradeoffs
```

### Episodes 500+: **Mastery**
```
Performance: Expert (50%+ win rate)
Discovery:
  ✓ Multiple victory paths
  ✓ Advanced card synergies
  ✓ Optimal timing sequences
  ✓ Creative problem solving
```

---

## 🗂️ Files That Enable Learning

### **1. Knowledge Base** (`data/knowledge_base.db`)
SQLite database storing:
```sql
-- Every screen state observed
game_states: id, timestamp, window_bounds, text_extracted, elements_detected

-- Every action taken
actions: id, state_id, type, parameters, timestamp

-- Sequences of actions
episodes: id, start_time, end_time, total_actions, outcome

-- Observations about the game
observations: id, category, content, timestamp
```

**Purpose**: Historical memory - enables learning from past experiences

### **2. Training Logs** (`data/logs/agent_*.jsonl`)
Detailed event stream:
```json
{"event": "vision_capture", "timestamp": "...", "ocr_text": [...], "color_regions": [...]}
{"event": "action_selected", "type": "DRAG", "from": [x1,y1], "to": [x2,y2]}
{"event": "action_executed", "success": true, "outcome": "..."}
```

**Purpose**: Debugging and analysis - understand what happened and why

### **3. TensorBoard Metrics** (`data/tensorboard/`)
Training statistics:
```
episode_actions: [25, 30, 45, 60, ...]  (Actions per episode)
episode_duration: [120, 150, 180, ...]  (Duration in seconds)
success_rate: [0.0, 0.0, 0.05, 0.1, ...] (Improving over time)
```

**Purpose**: Monitor learning progress - is the agent getting better?

### **4. Checkpoints** (`data/checkpoints/`)
Periodic snapshots:
```
checkpoint_ep20.txt:
  Episodes: 20
  Total Actions: 450
  Avg Duration: 135s
  Success Rate: 5%
```

**Purpose**: Resume training, track milestones, compare different training runs

### **5. Future: RL Model** (`models/rl_agent.pth`)
Trained neural network (created after 200+ episodes):
```
Architecture:
  Input: 512-dim state vector (vision + text + history)
  Hidden: 256 → 128 → 64 neurons
  Output: Action probabilities + Value estimate
```

**Purpose**: The "brain" - converts observations into intelligent actions

---

## 🎓 Why This Works Without Knowing Rules

### **1. Emergent Discovery**
The agent doesn't need rules programmed in. It discovers them:
```
Observation Pattern → Discovered Rule:
"Dragging Work card to Work verb 
 followed 80% of the time by Funds card"
→ RULE: Work produces Funds
```

### **2. Reward Shaping**
The agent gets feedback from:
- **Game state changes**: New cards = good, card decay = neutral, death = bad
- **Victory detection**: Winning screen = huge reward
- **Survival**: Longer episodes = better than short ones

### **3. Exploration vs Exploitation**
Early training: 90% random exploration, 10% learned behavior
Late training: 10% random exploration, 90% learned behavior

This ensures it:
- Discovers all mechanics (exploration)
- Optimizes known strategies (exploitation)

### **4. Generalization**
Neural networks find patterns:
```
Specific Experiences:
  "Passion + Reason → Enlightenment"
  "Health + Vitality → Vitality"
  "Funds + Work → More Funds"

Generalized Learning:
  "Combining similar cards amplifies effects"
  "Resource cards can be chained"
  "Some combinations unlock new mechanics"
```

---

## 🚀 Training Script Verification

### **Quick Test** (`./quick_train.sh`)
```bash
Episodes:     5
Max Actions:  20 per episode  
Duration:     2-3 minutes
Purpose:      Verify system works
```
✅ **Use this to**: Test after code changes, verify safety

### **Production Training** (`./start_training.sh`)
```bash
Episodes:     200
Max Actions:  150 per episode
Checkpoints:  Every 20 episodes
Duration:     1-2 hours
Purpose:      Collect serious training data
```
✅ **Use this for**: Real learning, RL model training prep

---

## 📈 Expected Results

### After Quick Test (5 episodes):
- ✓ TensorBoard shows 5 data points
- ✓ ~100 actions logged
- ✓ Database has screen states + actions
- ✓ No crashes or safety violations

### After Production Training (200 episodes):
- ✓ TensorBoard shows learning trends
- ✓ ~30,000 actions collected
- ✓ Rich dataset for RL training
- ✓ YOLO training data ready
- ✓ Clear patterns in logs

### After RL Model Training (future):
- ✓ Agent plays strategically (not randomly)
- ✓ Recognizes cards and verbs
- ✓ Manages resources intelligently
- ✓ Attempts victory conditions
- ✓ 10-30% win rate (vs 0% random)

---

## 🎯 Bottom Line

**Your agent learns Cultist Simulator the same way humans do:**

1. **Trial and error**: Try actions, see what happens
2. **Pattern recognition**: Notice what works, what fails
3. **Strategy building**: Combine patterns into sequences
4. **Optimization**: Refine strategies through practice
5. **Mastery**: Achieve victory through learned knowledge

**The difference**: Humans learn in ~10 hours of play. The AI needs ~500 episodes (~50-100 hours) because it starts with zero context and has no intuition about card games or narratives.

But once trained, it can play 24/7, explore every mechanic, and discover strategies humans might miss!

---

## 🔍 Next Steps

1. **Run production training**: `./start_training.sh`
2. **Monitor TensorBoard**: http://localhost:6006
3. **Watch for patterns**: Actions/episode should stabilize
4. **After 200 episodes**: Analyze data, prepare for RL training
5. **Train YOLO**: Teach visual recognition
6. **Train RL model**: Transform random exploration into strategic play

**Questions?** Check the logs, read the code, and remember: the AI is learning by doing, just like you did when you first played!
