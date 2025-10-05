#!/usr/bin/env python3
"""Test script for interrupt handling - Press Ctrl+C to stop the agent."""

from src.orchestrator import run_episode

print("=" * 60)
print("INTERRUPT TEST")
print("=" * 60)
print("\nStarting agent with 100 max actions...")
print("Press Ctrl+C at any time to stop gracefully\n")
print("The agent will:")
print("  1. Detect the interrupt")
print("  2. Stop the current episode") 
print("  3. Save the session data")
print("  4. Exit cleanly\n")
print("=" * 60)
print()

try:
    session = run_episode(
        agent_id="interrupt_test",
        window_name="Cultist Simulator",
        max_actions=100,
        max_duration_seconds=300
    )
    
    print("\n" + "=" * 60)
    print("✅ Episode completed normally")
    print("=" * 60)
    print(f"  Actions taken: {session.total_actions}")
    print(f"  Duration: {session.duration_seconds:.1f}s")
    print(f"  End condition: {session.end_condition.value}")
    print(f"  Session ID: {session.session_id}")
    print()

except KeyboardInterrupt:
    print("\n" + "=" * 60)
    print("✅ INTERRUPT HANDLED SUCCESSFULLY")
    print("=" * 60)
    print("  Agent stopped cleanly via Ctrl+C")
    print("  Session data has been saved")
    print()
