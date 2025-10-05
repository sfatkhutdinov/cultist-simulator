
# Implementation Plan: Autonomous AI Agent for Cultist Simulator

**Branch**: `001-autonomous-ai-agent` | **Date**: 2025-10-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-autonomous-ai-agent/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, or `AGENTS.md` for all other agents).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Build an autonomous AI agent that learns to play and win Cultist Simulator on macOS through self-discovery and experimentation. The agent will use computer vision to observe game state, reinforcement learning to develop strategies, NLP for narrative comprehension, and sandboxed macOS automation for safe game interaction. Key challenges include autonomous goal discovery, multi-dimensional performance tracking (survival time, win rate, resources, unique endings), full semantic understanding of narrative text, and 100% reliable safety containment to prevent system-level actions.

## Technical Context
**Language/Version**: Python 3.11+ (for AI/ML ecosystem, macOS automation, and rapid prototyping)  
**Primary Dependencies**: PyTorch/TensorFlow (RL), OpenCV (computer vision), Tesseract/EasyOCR (text extraction), transformers (NLP), pyautogui/Quartz (macOS automation)  
**Storage**: SQLite for knowledge base and session history; JSON for game state snapshots; pickle for model checkpoints  
**Testing**: pytest for unit/integration tests; custom test harness for agent behavior validation  
**Target Platform**: macOS 13+ (Ventura and later for modern accessibility APIs)
**Project Type**: single (Python AI agent with modular libraries)  
**Performance Goals**: <500ms action selection latency; <100ms knowledge base queries; 100-500 attempts to first win  
**Constraints**: 100% safety containment reliability; no game exits; semantic NLP for narrative; deterministic with seeded RNG  
**Scale/Scope**: Single-player game automation; ~10-20 distinct game mechanics to learn; multi-dimensional metrics tracking

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Library-First Architecture
- ✅ **PASS**: Design follows modular library structure
  - `vision_lib`: Game state capture and element detection (standalone, testable)
  - `automation_lib`: Safe macOS input simulation (standalone, testable)
  - `learning_lib`: RL agent and knowledge base (standalone, testable)
  - `nlp_lib`: Narrative text comprehension (standalone, testable)
  - `safety_lib`: Containment and constraint enforcement (standalone, testable)
  - Each library has clear purpose and well-defined boundaries

### II. CLI Interface Requirement
- ✅ **PASS**: Each library will expose CLI
  - `vision_lib`: `--capture-game-state` → JSON output of detected elements
  - `automation_lib`: `--simulate-click x y` → logs action to stdout
  - `learning_lib`: `--query-knowledge "game mechanic"` → JSON response
  - `nlp_lib`: `--analyze-text "narrative"` → JSON semantic analysis
  - `safety_lib`: `--validate-action "click x y"` → allow/block decision
  - Main agent orchestrator: `--run-episode` with JSON progress logs

### III. Test-First Development (NON-NEGOTIABLE)
- ✅ **PASS**: TDD workflow enforced
  - Contract tests for each library interface BEFORE implementation
  - Integration tests for library interactions BEFORE orchestration
  - Agent behavior tests (e.g., "agent improves over 10 episodes") BEFORE training loop
  - No implementation without failing tests first

### IV. Integration Testing Requirements
- ✅ **PASS**: Comprehensive integration testing
  - Vision ↔ Automation: Detect element → simulate click → verify state change
  - Learning ↔ Knowledge Base: Store session → query patterns → verify retrieval
  - NLP ↔ Learning: Parse narrative → extract goals → update strategy
  - Safety ↔ Automation: Validate all actions before execution
  - End-to-end: Full episode simulation with mocked game responses

### V. Observability and Debugging
- ✅ **PASS**: Structured logging throughout
  - All game state snapshots serialized to JSON with timestamps
  - All agent decisions logged with reasoning (which strategy, why, expected outcome)
  - All actions logged before/after execution with results
  - Knowledge base changes tracked with version history
  - Debug mode shows real-time perception pipeline (FR-030, NFR-008)

### Game Design Standards
- ✅ **PASS**: Aligned with game design principles
  - Learning algorithm uses seeded RNG for reproducible training runs
  - Knowledge base persists deterministic state for replay
  - Performance: <500ms action selection meets real-time requirement
  
### Additional Notes
- No constitutional violations identified
- All principles naturally align with AI agent architecture
- Safety containment (FR-004) ensures reliability (NFR-004)

**GATE RESULT: ✅ PASSED** - All constitutional principles satisfied; ready for Phase 0 research.

## Project Structure

### Documentation (this feature)
```
specs/001-autonomous-ai-agent/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   ├── vision_lib.md
│   ├── automation_lib.md
│   ├── learning_lib.md
│   ├── nlp_lib.md
│   └── safety_lib.md
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── vision/                 # Game state capture and element detection
│   ├── __init__.py
│   ├── screen_capture.py   # Screenshot and window management
│   ├── element_detector.py # Computer vision for UI elements
│   ├── ocr.py              # Text extraction from game
│   └── cli.py              # CLI interface
│
├── automation/             # Safe macOS input simulation
│   ├── __init__.py
│   ├── input_simulator.py  # Mouse/keyboard control
│   ├── window_manager.py   # Game window focus management
│   └── cli.py              # CLI interface
│
├── learning/               # RL agent and knowledge base
│   ├── __init__.py
│   ├── agent.py            # Main RL agent
│   ├── knowledge_base.py   # Game mechanics storage
│   ├── strategy.py         # Strategy evolution
│   ├── metrics.py          # Performance tracking
│   └── cli.py              # CLI interface
│
├── nlp/                    # Narrative text comprehension
│   ├── __init__.py
│   ├── text_analyzer.py    # Semantic understanding
│   ├── goal_extractor.py   # Extract objectives from text
│   └── cli.py              # CLI interface
│
├── safety/                 # Containment and constraint enforcement
│   ├── __init__.py
│   ├── constraint_checker.py  # Validate actions
│   ├── loop_detector.py       # Detect repetitive patterns
│   └── cli.py                 # CLI interface
│
├── orchestrator/           # Main agent orchestration
│   ├── __init__.py
│   ├── agent_runner.py     # Episode execution loop
│   └── cli.py              # Main CLI entry point
│
└── lib/                    # Shared utilities
    ├── logging_config.py   # Structured logging setup
    ├── config.py           # Configuration management
    └── types.py            # Shared type definitions

tests/
├── contract/               # Library interface contracts
│   ├── test_vision_contract.py
│   ├── test_automation_contract.py
│   ├── test_learning_contract.py
│   ├── test_nlp_contract.py
│   └── test_safety_contract.py
│
├── integration/            # Cross-library integration
│   ├── test_vision_automation.py
│   ├── test_learning_knowledge.py
│   ├── test_nlp_learning.py
│   └── test_safety_automation.py
│
└── unit/                   # Unit tests for each module
    ├── vision/
    ├── automation/
    ├── learning/
    ├── nlp/
    └── safety/

data/                       # Runtime data storage
├── knowledge_base.db       # SQLite knowledge base
├── sessions/               # Session recordings
├── models/                 # Trained model checkpoints
└── logs/                   # Structured log files
```

**Structure Decision**: Single project structure selected. This is a standalone Python AI agent with modular libraries. The vision, automation, learning, NLP, and safety components are all Python libraries within a single project, following constitutional principle I (Library-First Architecture). Each library is self-contained and independently testable, with clear CLI interfaces per principle II.

## Phase 0: Research & Technical Decisions

✅ **Completed** - See `research.md` for full details.

**Key Decisions Made**:
1. **RL Framework**: Stable-Baselines3 with PPO algorithm
2. **Computer Vision**: OpenCV + YOLOv8 for real-time element detection
3. **OCR**: EasyOCR for game font accuracy
4. **NLP**: sentence-transformers for semantic understanding without LLM overhead
5. **Automation**: Quartz (PyObjC) for native macOS control with safety hooks
6. **Storage**: SQLite + JSON for fast, embedded, crash-recoverable persistence
7. **Loop Detection**: Sliding window pattern matching with edit distance
8. **Performance**: Asynchronous perception pipeline with action queuing

All research findings documented with rationale, best practices, and risk mitigation strategies.

## Phase 1: Design Artifacts

✅ **Completed** - All design documents generated.

**Artifacts Created**:
1. **data-model.md**: 
   - 9 core entities (Agent, GameState, Action, Session, KnowledgeBase, Strategy, etc.)
   - Complete SQLite schema
   - Enumerations and value objects
   - Data flow and lifecycle documentation

2. **contracts/** directory (5 library contracts):
   - `vision_lib.md`: Game state capture and element detection interface
   - `automation_lib.md`: Safe input simulation interface with 100% safety validation
   - `learning_lib.md`: RL agent and knowledge base interface
   - `nlp_lib.md`: Semantic text analysis interface
   - `safety_lib.md`: Constraint validation interface

3. **quickstart.md**:
   - Setup and installation guide
   - TDD workflow instructions
   - CLI command reference
   - Debugging and performance optimization tips
   - Safety checklist

All contracts include:
- Public API functions with input/output specifications
- CLI interface definitions (JSON I/O per constitution)
- Error handling contracts
- Performance requirements
- Testing requirements
- Example usage

## Phase 2: Task Generation Approach
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

**Note**: This section is intentionally empty. Constitution Check passed with no violations. All design decisions align with constitutional principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md created
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md created
- [x] Phase 2: Task planning complete (/plan command - describe approach only) - See below
- [ ] Phase 3: Tasks generated (/tasks command) - Ready for /tasks
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (all principles align with AI agent architecture)
- [x] Post-Design Constitution Check: PASS (no violations introduced)
- [x] All NEEDS CLARIFICATION resolved (3 deferred to planning, now resolved)
- [x] Complexity deviations documented (none - design adheres to constitution)

---

## Phase 2: Task Generation Approach

**DO NOT CREATE tasks.md** - This phase only describes the approach for the `/tasks` command.

### Task Generation Strategy

The `/tasks` command will generate tasks following this approach:

1. **From Contracts** (5 libraries × contract test tasks):
   - Each library (vision, automation, learning, nlp, safety) gets contract test suite
   - Tests verify input/output contracts, error handling, performance requirements
   - Mark [P] for parallel execution (different files)

2. **From Data Model** (entity implementation tasks):
   - Implement core entities: Agent, GameState, Action, Session, KnowledgeBase, etc.
   - Each entity in separate file for parallel development
   - Include serialization, validation, behaviors

3. **Setup Tasks** (sequential, foundational):
   - Project structure setup
   - Database schema initialization
   - Model downloads (YOLO, NLP, OCR)
   - Configuration management

4. **Core Implementation Tasks** (per library):
   - Vision: screen capture, element detection, OCR integration
   - Automation: input simulation, safety validation hooks
   - Learning: RL agent, knowledge base, loop detection
   - NLP: text analysis, embedding generation, similarity search
   - Safety: constraint validation, blacklist enforcement

5. **Integration Tasks** (after core libraries):
   - Vision ↔ Automation integration
   - Learning ↔ Knowledge Base integration
   - Safety ↔ All libraries integration
   - Orchestrator assembly

6. **Polish Tasks**:
   - CLI implementations for each library
   - Logging and observability
   - Performance optimization
   - Documentation

### Task Ordering Principles

- **Dependencies First**: Setup → Core Libraries → Integration → Orchestration
- **TDD Required**: Test task before implementation task (constitution principle III)
- **Parallel Where Possible**: Different files/libraries marked [P]
- **Safety Critical**: Safety library tasks have high priority
- **Integration Last**: Integration tests after unit tests pass

### Expected Task Count

Estimated 145-155 tasks total (updated from initial 85-125 estimate):
- Setup: ~10 tasks
- Contract tests: ~26 tasks (5 per library + narrative decision test)
- Core implementation: ~50 tasks (including crash recovery, save game support, and subtasks T113a-f)
- Integration: ~15 tasks
- Polish: ~15 tasks (including validation tasks T138-T141)
- Performance/validation: ~8 tasks (multi-resolution, endurance, win validation)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
