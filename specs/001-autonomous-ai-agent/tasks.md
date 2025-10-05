# Tasks: Autonomous AI Agent for Cultist Simulator

**Input**: Design documents from `/specs/001-autonomous-ai-agent/`
**Prerequisites**: plan.md ✓, research.md ✓, data-mo### Orchestrator (src/orchestrator/)

- [x] **T105** Initialize orchestrator structure in src/orchestrator/__init__.py
- [x] **T106** Implement episode execution loop in src/orchestrator/agent_runner.py
- [x] **T107** Integrate vision → action selection → automation pipeline in src/orchestrator/agent_runner.py
- [x] **T108** Implement session recording and persistence in src/orchestrator/agent_runner.py
- [x] **T109** Implement training loop (100-500 episodes) in src/orchestrator/agent_runner.py
- [x] **T110** Implement real-time metrics tracking in src/orchestrator/agent_runner.py
- [x] **T111** Implement articulate_strategy() for human-readable output in src/orchestrator/agent_runner.py
- [x] **T112** Implement crash recovery and resume logic in src/orchestrator/agent_runner.py
- [x] **T113** Implement main orchestrator CLI in src/orchestrator/cli.pyontracts/ ✓

---

## Overview

This tasks document breaks down the implementation of an autonomous AI agent that learns to play Cultist Simulator on macOS. The agent uses computer vision, reinforcement learning, NLP, and safe automation libraries following a Test-Driven Development (TDD) workflow as required by the constitution.

**Tech Stack**: Python 3.11+, Stable-Baselines3, OpenCV, YOLOv8, EasyOCR, sentence-transformers, Quartz (PyObjC), SQLite

**Key Libraries**:
- `vision_lib`: Game state capture and element detection
- `automation_lib`: Safe macOS input simulation
- `learning_lib`: RL agent and knowledge base
- `nlp_lib`: Narrative text comprehension
- `safety_lib`: Constraint validation (100% reliability required)

---

## Phase 3.1: Setup

- [x] **T001** Create project directory structure per plan.md (src/, tests/, data/ directories)
- [x] **T002** Initialize Python 3.11+ project with virtual environment and requirements.txt
- [x] **T003** Install core dependencies (pytest, black, mypy, pylint)
- [ ] **T004** [P] Download YOLO model weights (yolov8n.pt) to models/ directory
- [ ] **T005** [P] Download sentence-transformers model (all-MiniLM-L6-v2) to models/ directory
- [ ] **T006** [P] Download EasyOCR model weights for English language
- [x] **T007** Initialize SQLite database schema from data-model.md in data/knowledge_base.db
- [x] **T008** Configure structured logging with JSON output to data/logs/
- [x] **T009** Create shared type definitions in src/lib/types.py (Point, Rect, enums)
- [x] **T010** Set up pytest configuration with coverage reporting

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL**: These tests MUST be written and MUST FAIL before ANY implementation. Constitution Principle III (Non-Negotiable).

### Contract Tests (Libraries)

- [x] **T011** [P] Contract test for vision_lib.capture_game_state() in tests/contract/test_vision_contract.py
- [x] **T012** [P] Contract test for vision_lib.detect_elements() in tests/contract/test_vision_contract.py
- [x] **T013** [P] Contract test for vision_lib.extract_text_regions() in tests/contract/test_vision_contract.py
- [x] **T014** [P] Contract test for automation_lib.simulate_click() in tests/contract/test_automation_contract.py
- [x] **T015** [P] Contract test for automation_lib.simulate_drag() in tests/contract/test_automation_contract.py
- [x] **T016** [P] Contract test for automation_lib.simulate_key_press() in tests/contract/test_automation_contract.py
- [x] **T017** [P] Contract test for learning_lib.select_action() in tests/contract/test_learning_contract.py
- [x] **T018** [P] Contract test for learning_lib.update_knowledge() in tests/contract/test_learning_contract.py
- [x] **T019** [P] Contract test for learning_lib.detect_loop() in tests/contract/test_learning_contract.py
- [x] **T020** [P] Contract test for nlp_lib.analyze_text() in tests/contract/test_nlp_contract.py
- [x] **T021** [P] Contract test for nlp_lib.extract_goals() in tests/contract/test_nlp_contract.py
- [x] **T022** [P] Contract test for safety_lib.validate_action() in tests/contract/test_safety_contract.py
- [x] **T023** [P] Contract test for safety_lib.is_within_bounds() in tests/contract/test_safety_contract.py

### Integration Tests

- [x] **T024** [P] Integration test: vision → automation (detect element → click) in tests/integration/test_vision_automation.py
- [x] **T025** [P] Integration test: learning → knowledge base (store/query session) in tests/integration/test_learning_knowledge.py
- [x] **T026** [P] Integration test: nlp → learning (extract goals → update strategy) in tests/integration/test_nlp_learning.py
- [x] **T027** [P] Integration test: safety → automation (validate → execute) in tests/integration/test_safety_automation.py
- [x] **T028** [P] Integration test: full episode simulation (mocked game) in tests/integration/test_episode_flow.py
- [ ] **T028a** [P] Integration test: Same game state with different narrative text → verify agent chooses different actions in tests/integration/test_narrative_decisions.py

### Safety Tests (CRITICAL - 100% Reliability Required)

- [x] **T029** [P] Safety test: block out-of-bounds clicks in tests/contract/test_safety_contract.py
- [x] **T030** [P] Safety test: block blacklisted keys (Cmd+Q, etc.) in tests/contract/test_safety_contract.py
- [x] **T031** [P] Safety test: block actions when window unfocused in tests/contract/test_safety_contract.py
- [x] **T032** [P] Safety test: enforce rate limiting in tests/contract/test_safety_contract.py
- [x] **T033** [P] Adversarial safety test: attempt to bypass all constraints in tests/contract/test_safety_contract.py

### Performance Tests

- [x] **T034** [P] Performance test: capture_game_state() <500ms in tests/performance/test_vision_performance.py
- [ ] **T035** [P] Performance test: knowledge query <100ms in tests/performance/test_learning_performance.py
- [x] **T036** [P] Performance test: safety validation <10ms in tests/performance/test_safety_performance.py

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

**User must verify tests are RED (failing) before proceeding with implementation tasks.**

### Shared Data Models & Utilities

- [x] **T037** [P] Implement Point and Rect value objects in src/lib/types.py
- [x] **T038** [P] Implement enums (ElementType, ActionType, CardState, etc.) in src/lib/types.py
- [x] **T039** [P] Implement GameState entity in src/lib/types.py
- [x] **T040** [P] Implement GameElement entity in src/lib/types.py
- [x] **T041** [P] Implement Action entity in src/lib/types.py
- [x] **T042** [P] Implement Card entity in src/lib/types.py
- [x] **T043** [P] Implement Session entity in src/lib/types.py
- [x] **T044** [P] Implement Agent entity in src/lib/types.py
- [x] **T045** [P] Implement Strategy entity in src/lib/types.py
- [x] **T046** [P] Implement PerformanceMetric entity in src/lib/types.py
- [x] **T047** [P] Logging configuration with structured JSON output in src/lib/logging_config.py
- [x] **T048** [P] Configuration management (load YAML configs) in src/lib/config.py

### Vision Library (src/vision/)

- [x] **T049** Initialize vision library structure and __init__.py in src/vision/__init__.py
- [x] **T050** Implement screen capture using Quartz in src/vision/screen_capture.py
- [x] **T051** Implement get_window_bounds() for game window location in src/vision/screen_capture.py
- [x] **T052** Implement YOLO-based element detection in src/vision/element_detector.py
- [x] **T053** Implement template matching for UI elements in src/vision/element_detector.py
- [x] **T054** Implement OCR text extraction using EasyOCR in src/vision/ocr.py
- [x] **T055** Implement capture_game_state() integrating all vision components in src/vision/__init__.py
- [x] **T056** Implement detect_elements() public interface in src/vision/__init__.py
- [x] **T057** Implement extract_text_regions() public interface in src/vision/__init__.py
- [x] **T058** Implement track_element_changes() state comparison in src/vision/__init__.py
- [ ] **T059** Implement vision library CLI in src/vision/cli.py with JSON I/O

### Automation Library (src/automation/)

- [x] **T060** Initialize automation library structure and __init__.py in src/automation/__init__.py
- [x] **T061** Implement Quartz-based mouse click simulation in src/automation/input_simulator.py
- [x] **T062** Implement Quartz-based mouse drag simulation in src/automation/input_simulator.py
- [x] **T063** Implement Quartz-based keyboard input simulation in src/automation/input_simulator.py
- [x] **T064** Implement window focus verification in src/automation/window_manager.py
- [x] **T065** Implement simulate_click() with safety pre-validation in src/automation/__init__.py
- [x] **T066** Implement simulate_drag() with bounds validation in src/automation/__init__.py
- [x] **T067** Implement simulate_key_press() with blacklist checking in src/automation/__init__.py
- [x] **T068** Implement wait() function in src/automation/__init__.py
- [ ] **T069** Implement emergency stop mechanism (F12 key listener) in src/automation/__init__.py
- [ ] **T070** Implement automation library CLI in src/automation/cli.py with JSON I/O

### Safety Library (src/safety/)

- [x] **T071** Initialize safety library structure and __init__.py in src/safety/__init__.py
- [x] **T072** Implement is_within_bounds() coordinate validation in src/safety/constraint_checker.py
- [x] **T073** Implement is_key_blacklisted() with forbidden key list in src/safety/constraint_checker.py
- [x] **T074** Implement check_rate_limit() action throttling in src/safety/constraint_checker.py
- [x] **T075** Implement validate_action() comprehensive validation in src/safety/constraint_checker.py
- [ ] **T076** [BLOCKING] Implement loop detection using sliding window (5-minute window, detect 3+ identical sequences) in src/safety/loop_detector.py
- [ ] **T077** [BLOCKING] Implement Levenshtein distance for pattern matching in src/safety/loop_detector.py
- [ ] **T078** Implement safety violation logging in src/safety/constraint_checker.py
- [ ] **T079** Implement safety library CLI in src/safety/cli.py with JSON I/O

### NLP Library (src/nlp/)

- [x] **T080** Initialize NLP library structure and __init__.py in src/nlp/__init__.py
- [x] **T081** Load sentence-transformers model in src/nlp/text_analyzer.py
- [x] **T082** Implement text embedding generation in src/nlp/text_analyzer.py
- [x] **T083** Implement semantic similarity search in src/nlp/text_analyzer.py
- [x] **T084** Implement analyze_text() with embeddings in src/nlp/__init__.py
- [x] **T085** Implement goal extraction from narrative text in src/nlp/goal_extractor.py
- [x] **T086** Implement extract_goals() public interface in src/nlp/__init__.py
- [x] **T087** Implement find_similar_narratives() with cosine similarity in src/nlp/__init__.py
- [x] **T088** Implement embedding cache for performance in src/nlp/text_analyzer.py
- [ ] **T089** Implement NLP library CLI in src/nlp/cli.py with JSON I/O

### Learning Library (src/learning/)

- [x] **T090** Initialize learning library structure and __init__.py in src/learning/__init__.py
- [ ] **T091** Set up Stable-Baselines3 PPO agent in src/learning/agent.py
- [ ] **T092** Implement custom gym environment for Cultist Simulator in src/learning/agent.py
- [x] **T093** Implement select_action() using trained policy in src/learning/__init__.py
- [x] **T094** Implement update_knowledge() for experience replay in src/learning/__init__.py
- [x] **T095** Initialize SQLite knowledge base connection in src/learning/knowledge_base.py
- [x] **T096** Implement store_session() to persist session data in src/learning/knowledge_base.py
- [x] **T097** Implement query_knowledge() for similarity search in src/learning/knowledge_base.py
- [ ] **T098** Implement store_mechanic() for game rules in src/learning/knowledge_base.py
- [x] **T099** Implement detect_loop() using action history in src/learning/__init__.py
- [ ] **T100** Implement Strategy entity CRUD operations in src/learning/strategy.py
- [ ] **T101** Implement strategy evolution (mutation, merging) in src/learning/strategy.py
- [ ] **T102** Implement PerformanceMetric tracking system in src/learning/metrics.py
- [ ] **T103** Implement multi-dimensional metrics (survival, win rate, resources, endings) in src/learning/metrics.py
- [ ] **T104** Implement learning library CLI in src/learning/cli.py with JSON I/O

### Orchestrator (Main Agent Runner)

- [ ] **T105** Initialize orchestrator structure in src/orchestrator/__init__.py
- [ ] **T106** Implement episode execution loop in src/orchestrator/agent_runner.py
- [ ] **T107** Integrate vision → action selection → automation pipeline in src/orchestrator/agent_runner.py
- [ ] **T108** Implement session recording and persistence in src/orchestrator/agent_runner.py
- [ ] **T109** Implement training loop (100-500 episodes) in src/orchestrator/agent_runner.py
- [ ] **T110** Implement real-time metrics tracking in src/orchestrator/agent_runner.py
- [ ] **T111** Implement articulate_strategy() for human-readable output in src/orchestrator/agent_runner.py
- [ ] **T112** Implement crash recovery and resume logic in src/orchestrator/agent_runner.py
- [ ] **T113** Implement main orchestrator CLI in src/orchestrator/cli.py
- [ ] **T113a** Implement crash detection (monitor game window/process status) in src/orchestrator/agent_runner.py
- [ ] **T113b** Implement auto-save agent state every N actions (configurable checkpoint frequency) in src/orchestrator/agent_runner.py
- [ ] **T113c** Implement resume from last checkpoint on restart in src/orchestrator/agent_runner.py
- [ ] **T113d** Implement load_save_game() to start from saved game state in src/orchestrator/agent_runner.py
- [ ] **T113e** Implement create_save_game() for training checkpoint persistence in src/orchestrator/agent_runner.py
- [ ] **T113f** Integration test: Load save game → verify agent state consistency in tests/integration/test_save_game.py

---

## Phase 3.4: Integration

- [ ] **T114** Connect vision_lib to automation_lib (element detection → click targeting)
- [ ] **T115** Connect learning_lib to knowledge_base (session persistence)
- [ ] **T116** Connect nlp_lib to learning_lib (goal extraction → strategy update)
- [ ] **T117** Connect safety_lib to automation_lib (pre-validation hooks)
- [ ] **T118** Integrate all libraries in orchestrator main loop
- [ ] **T119** Set up TensorBoard logging for training metrics
- [ ] **T120** Implement session replay functionality
- [ ] **T121** Add graceful shutdown on crash/interrupt
- [ ] **T122** Configure macOS permissions check on startup

---

## Phase 3.5: Polish

- [ ] **T123** [P] Unit test GameState serialization in tests/unit/test_gamestate.py
- [ ] **T124** [P] Unit test Action validation logic in tests/unit/test_action.py
- [ ] **T125** [P] Unit test Strategy evolution in tests/unit/test_strategy.py
- [ ] **T126** [P] Unit test KnowledgeBase queries in tests/unit/test_knowledge.py
- [ ] **T127** Optimize vision pipeline for <500ms latency
- [ ] **T128** Optimize knowledge base queries for <100ms response
- [ ] **T129** Profile and optimize critical path bottlenecks
- [ ] **T130** Add comprehensive error handling and recovery
- [ ] **T131** Generate API documentation from docstrings
- [ ] **T132** Update quickstart.md with final setup instructions
- [ ] **T133** Create example configs for different training scenarios
- [ ] **T134** Run end-to-end test with actual Cultist Simulator game (success criteria: agent executes 10+ actions without crash)
- [ ] **T134a** Test vision pipeline across multiple resolutions (1920x1080, 2560x1440, 3840x2160) in tests/performance/test_multi_resolution.py
- [ ] **T135** Verify all safety constraints with adversarial testing
- [ ] **T136** Code cleanup: remove duplication, improve naming
- [ ] **T137** Final linting and type checking (mypy, black, pylint)

---

## Dependencies

### Critical Path
```
Setup (T001-T010)
  ↓
Tests Written (T011-T036) ← MUST FAIL before implementation
  ↓
Data Models (T037-T048) ← Blocks all library implementations
  ↓
Library Implementations (T049-T104) ← Can be parallel per library
  ↓
Integration (T114-T122)
  ↓
Polish (T123-T137)
```

### Detailed Dependencies

**Setup Phase**:
- T001-T010 have no dependencies (can run in order or parallel where marked [P])

**Test Phase**:
- T011-T036 depend on T009 (type definitions for test fixtures)
- All tests MUST fail before proceeding to T037

**Core Implementation**:
- T049-T059 (vision) depend on T037-T040 (GameState, GameElement)
- T060-T070 (automation) depend on T041 (Action), T073 (safety validation)
- T071-T079 (safety) depend on T041 (Action) only
- T080-T089 (NLP) have minimal dependencies (can start early)
- T090-T104 (learning) depend on T043-T046 (Session, Agent, Strategy, Metrics)
- T105-T113 (orchestrator) depend on ALL libraries (T049-T104)

**Integration Phase**:
- T114-T122 depend on all Phase 3.3 tasks completing
- **CRITICAL**: T114-T118 are BLOCKED by T076-T077 (loop detection must be complete for integration)

**Polish Phase**:
- T123-T137 depend on integration completing

---

## Parallel Execution Examples

### Parallel Batch 1: Model Downloads (after T003)
```bash
# Can run simultaneously - different files, no dependencies
Task T004: "Download YOLO model weights to models/ directory"
Task T005: "Download sentence-transformers model to models/ directory"
Task T006: "Download EasyOCR model weights for English"
```

### Parallel Batch 2: Contract Tests (after T009)
```bash
# All contract tests can run in parallel - independent test files
Task T011: "Contract test vision_lib.capture_game_state() in tests/contract/test_vision_contract.py"
Task T012: "Contract test vision_lib.detect_elements() in tests/contract/test_vision_contract.py"
Task T014: "Contract test automation_lib.simulate_click() in tests/contract/test_automation_contract.py"
Task T017: "Contract test learning_lib.select_action() in tests/contract/test_learning_contract.py"
Task T020: "Contract test nlp_lib.analyze_text() in tests/contract/test_nlp_contract.py"
Task T022: "Contract test safety_lib.validate_action() in tests/contract/test_safety_contract.py"
# ... etc for all T011-T023
```

### Parallel Batch 3: Data Models (after tests fail)
```bash
# Entity implementations - different files, can be parallel
Task T037: "Implement Point and Rect value objects in src/lib/types.py"
Task T039: "Implement GameState entity in src/lib/types.py"
Task T040: "Implement GameElement entity in src/lib/types.py"
Task T041: "Implement Action entity in src/lib/types.py"
Task T042: "Implement Card entity in src/lib/types.py"
# Note: T037-T048 all modify types.py, so cannot truly parallelize
# Split into sequential batches or create separate files per entity
```

### Parallel Batch 4: Library Implementations (after T048)
```bash
# Different libraries can be built in parallel by different developers/agents
# Vision Library Tasks (T049-T059)
# Automation Library Tasks (T060-T070) - BUT depends on T071-T075 (safety) first
# Safety Library Tasks (T071-T079) - Should go FIRST
# NLP Library Tasks (T080-T089)
# Learning Library Tasks (T090-T104)

# Recommended: Safety → Vision & NLP in parallel → Automation → Learning → Orchestrator
```

---

## Task Execution Notes

### TDD Enforcement (Constitutional Requirement)
1. Write test (e.g., T011)
2. Get user approval of test
3. Run test - MUST FAIL (RED)
4. Implement feature (e.g., T049-T055 for vision)
5. Run test - MUST PASS (GREEN)
6. Refactor while keeping tests green

### Parallel Execution Guidelines
- **[P] marker**: Task can run in parallel with other [P] tasks
- **Same file conflict**: Multiple [P] tasks for same file (e.g., T037-T048 all edit types.py) should be batched sequentially or files split
- **Library isolation**: Different libraries (vision, automation, etc.) are independent and can be built in parallel
- **Integration last**: Cannot parallelize integration tasks (T114-T122)

### Safety-Critical Tasks
- T029-T033 (safety tests) MUST achieve 100% reliability
- T071-T079 (safety implementation) has highest priority
- T135 (adversarial testing) is MANDATORY before deployment

### Performance Validation
- T034: vision <500ms (NFR-001)
- T035: knowledge query <100ms (NFR-003)
- T036: safety validation <10ms (critical path)
- T127-T129: Optimize if benchmarks not met

---

## Validation Checklist

Before declaring tasks complete:

- [x] All 5 library contracts have corresponding test tasks (T011-T023)
- [x] All 9 entities from data-model.md have implementation tasks (T037-T046)
- [x] All tests come before corresponding implementation tasks (TDD enforced)
- [x] All [P] tasks are truly independent (different files or no data dependencies)
- [x] Each task specifies exact file path
- [x] Safety tests have 100% reliability requirement documented (T029-T033, T135)
- [x] Performance tests match NFR requirements (T034-T036)
- [x] Integration tests cover all library pairs (T024-T028, T114-T118)
- [x] CLI implementations for all 5 libraries (T059, T070, T079, T089, T104)

---

## Estimated Timeline

- **Setup**: 1-2 days (T001-T010)
- **Test Writing**: 3-5 days (T011-T036) - Comprehensive test coverage
- **Data Models**: 2-3 days (T037-T048)
- **Core Libraries**: 15-20 days (T049-T104) - Largest phase
  - Vision: 3-4 days
  - Automation: 3-4 days
  - Safety: 2-3 days
  - NLP: 2-3 days
  - Learning: 4-5 days
  - Orchestrator: 2-3 days
- **Integration**: 3-5 days (T114-T122)
- **Polish**: 2-3 days (T123-T137)

**Total**: ~30-40 days for full implementation

**To First Win**: Agent should achieve first win within 100-500 game attempts after training begins (FR-026)

---

## Ready for Execution

All tasks are now defined and ready for implementation. Proceed with:
1. Setup phase (T001-T010)
2. Write ALL tests first (T011-T036) and get user approval
3. Verify tests FAIL
4. Begin implementation following dependency order

**Next Command**: Begin with `T001: Create project directory structure`