<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.0.1
- Modified principles: None
- Added sections: None
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md: Updated version reference from v2.1.1 to v1.0.1
  ✅ spec-template.md: Scope/requirements alignment confirmed
  ✅ tasks-template.md: Task categorization reflects principle-driven task types
  ✅ agent-file-template.md: No constitution references
- Follow-up TODOs: None
- Change type: PATCH (version reference correction only)
-->

# Cultist Simulator Constitution

## Core Principles

### I. Library-First Architecture
Every feature MUST start as a standalone library with clear boundaries. Libraries MUST be self-contained, independently testable, and thoroughly documented. Each library MUST have a single, well-defined purpose—no organizational-only libraries are permitted.

**Rationale**: Modular design ensures testability, reusability, and maintainability. This is particularly crucial for a game like Cultist Simulator where complex systems (rituals, cards, narrative) need to interact cleanly.

### II. CLI Interface Requirement
Every library MUST expose its functionality via a command-line interface. Text-based input/output protocol MUST be followed: stdin/arguments → stdout, errors → stderr. Both JSON and human-readable formats MUST be supported.

**Rationale**: CLI interfaces ensure debuggability and enable automation. For game development, this allows testing of game mechanics independently of UI/graphics.

### III. Test-First Development (NON-NEGOTIABLE)
Test-Driven Development is MANDATORY: Tests MUST be written → User approved → Tests MUST fail → Then implement. The Red-Green-Refactor cycle MUST be strictly enforced. No code merges without corresponding tests.

**Rationale**: Games have complex state interactions and narrative dependencies. TDD ensures mechanics work as intended and prevents regressions in game balance or story flow.

### IV. Integration Testing Requirements
Integration tests are REQUIRED for: New library contract tests, contract changes, inter-service communication, and shared game schemas (cards, rituals, outcomes). Cross-system testing MUST verify game state consistency.

**Rationale**: Cultist Simulator's interconnected systems (time passage, ritual outcomes, narrative progression) require comprehensive integration testing to ensure emergent gameplay works correctly.

### V. Observability and Debugging
All text-based I/O MUST ensure debuggability. Structured logging is REQUIRED for all game state changes, user actions, and system events. Game state MUST be serializable and inspectable at any point.

**Rationale**: Complex narrative games require detailed debugging capabilities to trace unexpected behaviors, balance issues, and story progression problems.

## Game Design Standards

Game mechanics MUST be implemented as pure functions where possible. Random number generation MUST use seeded, reproducible algorithms. All game state transitions MUST be deterministic given the same inputs and random seed.

Save game compatibility MUST be maintained within major versions. Breaking changes to save format require major version increment and migration path documentation.

Performance requirements: Game state updates MUST complete within 16ms for 60fps target. Memory usage MUST not exceed 512MB for base gameplay on target platforms.

## Development Workflow

All features MUST follow the Specify workflow: /specify → /clarify → /plan → /tasks → implementation. Each phase MUST complete successfully before proceeding to the next.

Code reviews MUST verify constitutional compliance before merge. All constitutional violations MUST be documented and justified, or the code MUST be refactored to comply.

Version control MUST follow semantic versioning: MAJOR for breaking changes to save format or core mechanics, MINOR for new features or content, PATCH for bug fixes and balance adjustments.

## Governance

This Constitution supersedes all other development practices and guidelines. All pull requests and code reviews MUST verify compliance with these principles.

Amendments to this Constitution require documentation of impact, stakeholder approval, and a clear migration plan for affected systems. Constitutional violations MUST be justified with technical necessity and remediation timeline.

Complexity that violates constitutional principles MUST be justified or the approach MUST be simplified. Use template-based guidance files for runtime development decisions aligned with these principles.

**Version**: 1.0.1 | **Ratified**: 2025-10-04 | **Last Amended**: 2025-10-06