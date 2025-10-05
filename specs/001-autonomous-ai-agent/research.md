# Research & Technical Decisions

**Feature**: Autonomous AI Agent for Cultist Simulator  
**Date**: 2025-10-04  
**Phase**: 0 - Technical Research

## Research Areas

### 1. Reinforcement Learning Framework Selection

**Decision**: Use Stable-Baselines3 (SB3) with PPO algorithm

**Rationale**:
- **SB3**: Well-maintained, production-ready RL library built on PyTorch
- **PPO (Proximal Policy Optimization)**: 
  - Sample-efficient for complex decision spaces
  - Stable training with fewer hyperparameters than DQN
  - Handles continuous/discrete action spaces
  - Good for sparse reward environments (perfect for game-playing)
  - **Exploration/Exploitation**: PPO uses entropy regularization to balance exploration vs exploitation automatically; no epsilon-greedy needed
- **Alternatives considered**:
  - Ray RLlib: More scalable but overkill for single-game agent
  - TensorFlow Agents: Less Python-native, smaller community
  - Custom implementation: Too risky for timeline constraints

**Best Practices**:
- Use environment wrappers for game state normalization
- Implement custom reward shaping for multi-dimensional metrics
- Enable tensorboard logging for training visualization
- Save checkpoints every N episodes for recovery

### 2. Computer Vision for Game State Capture

**Decision**: OpenCV + Template Matching + YOLO-based object detection

**Rationale**:
- **OpenCV**: Industry standard for image processing, excellent macOS support
- **Template Matching**: Fast for detecting UI buttons, icons with fixed appearance
- **YOLOv8 (via ultralytics)**: 
  - Real-time object detection for game elements (cards, timers)
  - Can be trained on custom dataset of game screenshots
  - <50ms inference time meets performance requirements
- **Alternatives considered**:
  - Pure OCR: Insufficient for visual elements like cards/icons
  - Segmentation models: Too slow for real-time gameplay
  - Pre-trained ImageNet models: Don't understand game-specific elements

**Best Practices**:
- Capture game window at fixed resolution for consistency
- Use color space conversion (HSV) for robust element detection
- Cache detected element positions to reduce processing
- Implement confidence thresholds to avoid false positives

### 3. Text Extraction and NLP

**Decision**: EasyOCR for text extraction + sentence-transformers for semantic understanding

**Rationale**:
- **EasyOCR**: 
  - Better accuracy than Tesseract on game fonts
  - GPU acceleration available
  - Pre-trained on 80+ languages (handles stylized game text)
- **sentence-transformers (all-MiniLM-L6-v2)**:
  - Lightweight BERT-based model for semantic similarity
  - Can compare narrative text to known patterns
  - Enables "understanding" through embedding similarity
  - 384-dimensional embeddings fit in memory
- **Alternatives considered**:
  - Full GPT/LLM: Too slow (<500ms constraint), expensive
  - Keyword extraction only: Insufficient for semantic understanding (clarification requirement)
  - spaCy NER: Doesn't provide semantic similarity

**Best Practices**:
- Pre-process OCR regions to improve accuracy (threshold, denoise)
- Build embedding index of known game narratives
- Use cosine similarity to match new text to known patterns
- Cache embeddings for repeated text to save computation

### 4. macOS Automation and Safety Containment

**Decision**: Quartz (PyObjC) for low-level control + custom safety validator

**Rationale**:
- **Quartz/PyObjC**:
  - Direct access to macOS Core Graphics for precise control
  - Can programmatically get window bounds for containment
  - Supports CGEvent for keyboard/mouse simulation
  - More reliable than pyautogui for macOS-specific behavior
- **Safety Architecture**:
  - Pre-validation layer that checks all actions against window bounds
  - Blacklist of dangerous key combinations (Cmd+Q, Cmd+W, etc.)
  - Monitor window focus and abort if game loses focus
  - Rate limiting to prevent runaway automation
- **Alternatives considered**:
  - pyautogui: Cross-platform but less macOS-native, harder to enforce bounds
  - AppleScript: Too high-level, limited control
  - Accessibility API: More complex, designed for assistive tech

**Best Practices**:
- Always get fresh window bounds before each action
- Log all validated/blocked actions for audit trail
- Implement emergency stop signal (e.g., specific key press)
- Test containment with adversarial action sequences

### 5. Knowledge Base Storage

**Decision**: SQLite with custom schema + JSON for structured data

**Rationale**:
- **SQLite**:
  - Zero-configuration, embedded database
  - ACID compliance for crash recovery
  - Fast queries (<100ms requirement)
  - Portable file format for backup/sharing
- **Schema Design**:
  - `game_mechanics`: Discovered rules and patterns
  - `sessions`: Episode recordings with outcomes
  - `strategies`: Evolved strategy configurations
  - `state_transitions`: Observed cause-effect relationships
- **JSON Fields**:
  - Game states (complex nested structures)
  - Action sequences (variable length)
  - Narrative text (unstructured)

**Best Practices**:
- Index on frequently queried fields (mechanic_type, session_id)
- Use transactions for multi-record updates
- Implement write-ahead logging for crash recovery
- Periodic vacuum for performance maintenance

### 6. Loop Detection Algorithm

**Decision**: Sliding window pattern matching with edit distance

**Rationale**:
- **Algorithm**:
  - Track last N actions (window size ~20-50)
  - Compute Levenshtein distance between recent window and historical windows
  - If similarity > 80% and no progress (same game state), flag as loop
  - Trigger exploration boost or strategy switch
- **Why This Works**:
  - Catches exact repetitions and near-repetitions
  - Configurable sensitivity via window size and threshold
  - Low computational overhead (<1ms per check)
- **Alternatives considered**:
  - State-only loop detection: Misses action loops that change state slightly
  - Neural loop prediction: Too complex for reliability requirement

**Best Practices**:
- Different thresholds for different game phases (exploration vs. exploitation)
- Log loop events with context for debugging
- Implement gradual exploration increase (not abrupt strategy change)

### 7. Multi-Dimensional Metrics Tracking

**Decision**: Custom MetricsTracker class with real-time aggregation

**Rationale**:
- **Metrics to Track**:
  - Survival time: Duration from game start to game-over
  - Win rate: Percentage of episodes ending in win state
  - Resources accumulated: In-game wealth/assets at episode end
  - Unique endings: Count of distinct win conditions discovered
- **Implementation**:
  - In-memory aggregation during episode
  - Batch write to SQLite at episode end
  - Rolling averages for trend analysis (last 10, 50, 100 episodes)
  - Export to CSV/JSON for external analysis

**Best Practices**:
- Use moving averages to smooth noisy metrics
- Implement min/max/median tracking for distribution analysis
- Create visualization hooks for Tensorboard
- Store raw episode data for post-hoc analysis

### 8. Action Latency Optimization

**Decision**: Asynchronous perception pipeline with action queuing

**Rationale**:
- **Architecture**:
  - Vision processing runs in background thread (continuous screen capture)
  - RL agent queries latest cached game state (no blocking)
  - Action execution happens synchronously (safety critical)
  - Target: 200-300ms typical, <500ms worst case
- **Optimizations**:
  - Cache detected elements between frames
  - Use GPU for YOLO inference
  - Parallelize OCR across text regions
  - Pre-load NLP model embeddings

**Best Practices**:
- Profile critical path to identify bottlenecks
- Implement timeout fallbacks if processing exceeds budget
- Log latency metrics per component for optimization
- Use thread pools to avoid thread creation overhead

## Technical Stack Summary

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **RL Framework** | Stable-Baselines3 (PPO) | Sample-efficient, stable, production-ready |
| **Computer Vision** | OpenCV + YOLOv8 | Fast, accurate, custom-trainable |
| **OCR** | EasyOCR | Better game font accuracy than Tesseract |
| **NLP** | sentence-transformers | Semantic understanding without LLM overhead |
| **Automation** | Quartz (PyObjC) | Native macOS control with safety hooks |
| **Storage** | SQLite + JSON | Fast, embedded, crash-recoverable |
| **Metrics** | Custom tracker + Tensorboard | Real-time monitoring and analysis |
| **Testing** | pytest + custom harness | TDD-compatible, behavior validation |

## Open Questions for Phase 1

1. **Custom YOLO Training**: How many labeled screenshots needed for game element detection?
   - Research suggests 300-500 images per element class for transfer learning from COCO weights
   - Plan for manual labeling session or semi-automated labeling pipeline

2. **Reward Function Design**: How to balance multi-dimensional metrics in single reward signal?
   - Consider weighted sum vs. Pareto optimization
   - May need to experiment with different reward shaping strategies

3. **NLP Embedding Index Size**: How many unique narrative patterns exist in Cultist Simulator?
   - Need to estimate from game data analysis
   - Affects memory requirements and similarity search performance

4. **Safety Validation Performance**: Can we validate actions within acceptable latency?
   - Constraint checking must be <10ms to stay within budget
   - Need to benchmark window bounds lookup + blacklist checking

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| Vision processing too slow | Use hardware acceleration, implement caching, reduce resolution if needed |
| RL training doesn't converge | Implement curriculum learning, start with simpler sub-goals |
| Safety containment failure | Multiple validation layers, extensive adversarial testing |
| Knowledge base grows too large | Implement forgetting/pruning mechanisms, periodic archival |
| NLP model insufficient for narrative | Fall back to pattern matching, consider fine-tuning on game data |

## Next Steps (Phase 1)

1. Design detailed data models for entities (Agent, GameState, Action, etc.)
2. Define library contracts (input/output schemas, error handling)
3. Create quickstart guide for local development setup
4. Generate initial test cases for TDD workflow
