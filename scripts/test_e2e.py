#!/usr/bin/env python3
"""
End-to-End Test Script - T134

Tests the AI agent with the actual Cultist Simulator game.

SUCCESS CRITERIA:
- Agent executes 10+ actions without crashing
- Vision pipeline captures game state successfully
- Actions are executed safely within game window
- All safety constraints are respected
- Session is logged and can be replayed

Usage:
    python3 scripts/test_e2e.py [options]

Options:
    --actions NUM       Number of actions to execute (default: 10)
    --window NAME       Game window name (default: "Cultist Simulator")
    --dry-run           Test without actually clicking (safety test)
    --test-mode         Use random actions (no trained model required)
    --verbose           Show detailed logging
    --save-session      Save session for replay
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.vision import capture_game_state, detect_elements, get_window_bounds
from src.automation import simulate_click, simulate_key_press, check_window_focus
from src.safety import validate_action
from src.learning import select_action, store_session, enable_test_mode
from src.lib.types import ActionType, Point, Session
from src.lib.logging_config import configure_logging

# Initialize logger
logger = configure_logging(log_level="INFO", log_to_file=True)


class E2ETestRunner:
    """End-to-end test runner for Cultist Simulator AI agent."""

    def __init__(self, window_name="Cultist Simulator", max_actions=10, dry_run=False, test_mode=False):
        self.window_name = window_name
        self.max_actions = max_actions
        self.dry_run = dry_run
        self.test_mode = test_mode
        self.actions_executed = 0
        self.actions_blocked = 0
        self.errors = []
        self.session_data = {
            "start_time": datetime.now().isoformat(),
            "window_name": window_name,
            "actions": [],
            "errors": [],
            "performance": {},
        }
        
        # Enable test mode in learning module if requested
        if test_mode:
            enable_test_mode(True)
            logger.info("test_mode_enabled", description="Using random actions for testing")

    def check_prerequisites(self):
        """Check if game window is available and accessible."""
        logger.info("Checking prerequisites...")

        # Check if window exists
        try:
            window_bounds = get_window_bounds(self.window_name)
            if window_bounds is None:
                logger.error(f"❌ Game window '{self.window_name}' not found")
                logger.info(
                    "Available windows: (Check Activity Monitor or use window_manager.py to list)"
                )
                return False

            logger.info(f"✅ Found game window: {window_bounds}")
            self.session_data["window_bounds"] = {
                "x": window_bounds.x,
                "y": window_bounds.y,
                "width": window_bounds.width,
                "height": window_bounds.height,
            }

        except Exception as e:
            logger.error(f"❌ Error checking window: {e}")
            self.errors.append(f"Window check failed: {e}")
            return False

        # Check if window is focused
        try:
            is_focused = check_window_focus(self.window_name)
            if not is_focused:
                logger.warning(f"⚠️  Window '{self.window_name}' is not focused")
                logger.info("Please click on the game window and run this script again")
                return False
            logger.info("✅ Window is focused")
        except Exception as e:
            logger.warning(f"⚠️  Could not verify window focus: {e}")
            # Continue anyway - focus check might not be critical

        return True

    def capture_and_analyze_state(self):
        """Capture game state and analyze elements."""
        logger.info("Capturing game state...")

        start_time = time.perf_counter()
        try:
            game_state = capture_game_state(self.window_name)
            capture_time = (time.perf_counter() - start_time) * 1000

            if game_state is None:
                logger.error("❌ Failed to capture game state")
                return None, None

            logger.info(f"✅ Captured game state in {capture_time:.2f}ms")

            # Log what we detected
            if hasattr(game_state, "elements"):
                logger.info(f"   Detected {len(game_state.elements)} elements")
            if hasattr(game_state, "text_regions"):
                logger.info(f"   Extracted {len(game_state.text_regions)} text regions")

            return game_state, capture_time

        except Exception as e:
            logger.error(f"❌ Error capturing state: {e}")
            self.errors.append(f"State capture failed: {e}")
            return None, None

    def select_and_validate_action(self, game_state, window_bounds):
        """Select action and validate with safety checks."""
        logger.info("Selecting action...")

        try:
            # Select action using learning agent
            action = select_action(game_state)

            if action is None:
                logger.warning("⚠️  No action selected")
                return None

            logger.info(f"✅ Selected action: {action}")

            # Validate action with safety system
            action_dict = {
                "action_type": action.action_type,
                "point": action.parameters.get("point", Point(100, 100)),
            }

            context = {"window_bounds": window_bounds, "window_focused": True}

            validation = validate_action(action_dict, context)

            if not validation.is_allowed:
                logger.warning(
                    f"⚠️  Action blocked by safety: {validation.blocked_reason}"
                )
                self.actions_blocked += 1
                return None

            logger.info("✅ Action validated by safety system")
            return action

        except Exception as e:
            logger.error(f"❌ Error selecting/validating action: {e}")
            self.errors.append(f"Action selection failed: {e}")
            return None

    def execute_action(self, action, window_bounds):
        """Execute the validated action."""
        if self.dry_run:
            logger.info("🔍 DRY RUN: Would execute action")
            return True

        logger.info("Executing action...")

        try:
            start_time = time.perf_counter()

            # Execute based on action type
            action_type = action.action_type

            if action_type == ActionType.CLICK:
                point = action.parameters.get("point", Point(100, 100))
                result = simulate_click(point, "left", window_bounds)

            elif action_type == ActionType.KEY_PRESS:
                key = action.parameters.get("key", "space")
                modifiers = action.parameters.get("modifiers", [])
                result = simulate_key_press(key, modifiers, window_bounds)

            else:
                logger.warning(f"⚠️  Unsupported action type: {action_type}")
                return False

            execution_time = (time.perf_counter() - start_time) * 1000

            if hasattr(result, "success") and result.success:
                logger.info(
                    f"✅ Action executed successfully in {execution_time:.2f}ms"
                )
                self.actions_executed += 1
                return True
            else:
                logger.warning(f"⚠️  Action execution failed: {result}")
                return False

        except Exception as e:
            logger.error(f"❌ Error executing action: {e}")
            self.errors.append(f"Action execution failed: {e}")
            return False

    def run_test_cycle(self):
        """Run one complete test cycle."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Test Cycle {self.actions_executed + 1}/{self.max_actions}")
        logger.info(f"{'='*60}")

        # Get window bounds
        window_bounds = get_window_bounds(self.window_name)
        if window_bounds is None:
            logger.error("❌ Lost game window")
            return False

        # Capture state
        game_state, capture_time = self.capture_and_analyze_state()
        if game_state is None:
            return False

        # Select and validate action
        action = self.select_and_validate_action(game_state, window_bounds)
        if action is None:
            logger.warning("⚠️  Skipping this cycle (no valid action)")
            return True  # Not a failure, just skip

        # Execute action
        success = self.execute_action(action, window_bounds)

        # Record action
        self.session_data["actions"].append(
            {
                "cycle": self.actions_executed + (1 if success else 0),
                "timestamp": datetime.now().isoformat(),
                "action": str(action),
                "success": success,
                "capture_time_ms": capture_time if capture_time else 0,
            }
        )

        # Wait between actions (safety delay)
        if success and not self.dry_run:
            delay = 1.0  # 1 second between actions
            logger.info(f"⏱️  Waiting {delay}s before next action...")
            time.sleep(delay)

        return success

    def run(self):
        """Run the complete end-to-end test."""
        logger.info("\n" + "=" * 60)
        logger.info("END-TO-END TEST - Cultist Simulator AI Agent")
        logger.info("=" * 60)
        logger.info(f"Window: {self.window_name}")
        logger.info(f"Target Actions: {self.max_actions}")
        logger.info(f"Dry Run: {self.dry_run}")
        logger.info(f"Test Mode: {self.test_mode} {'(random actions)' if self.test_mode else '(requires trained model)'}")
        logger.info("=" * 60 + "\n")

        # Check prerequisites
        if not self.check_prerequisites():
            logger.error("\n❌ Prerequisites check failed. Exiting.")
            return False

        logger.info("\n✅ Prerequisites passed. Starting test...\n")

        # Run test cycles
        cycles_attempted = 0
        while (
            self.actions_executed < self.max_actions
            and cycles_attempted < self.max_actions * 2
        ):
            cycles_attempted += 1

            try:
                success = self.run_test_cycle()
                if not success:
                    logger.warning("⚠️  Cycle failed, but continuing...")

            except KeyboardInterrupt:
                logger.info("\n\n⚠️  Test interrupted by user")
                break

            except Exception as e:
                logger.error(f"\n❌ Unexpected error in cycle: {e}")
                self.errors.append(f"Cycle {cycles_attempted} error: {e}")
                break

        # Generate report
        self.generate_report()

        # Determine success - must execute the requested number of actions without errors
        success = self.actions_executed >= self.max_actions and len(self.errors) == 0

        if success:
            logger.info("\n" + "=" * 60)
            logger.info("✅ END-TO-END TEST PASSED")
            logger.info("=" * 60)
        else:
            logger.info("\n" + "=" * 60)
            logger.info("❌ END-TO-END TEST FAILED")
            logger.info("=" * 60)

        return success

    def generate_report(self):
        """Generate test report."""
        logger.info("\n" + "=" * 60)
        logger.info("TEST REPORT")
        logger.info("=" * 60)

        logger.info(f"\n📊 Statistics:")
        logger.info(f"   Actions Executed: {self.actions_executed}/{self.max_actions}")
        logger.info(f"   Actions Blocked:  {self.actions_blocked}")
        logger.info(f"   Errors:           {len(self.errors)}")

        if self.errors:
            logger.info(f"\n❌ Errors:")
            for i, error in enumerate(self.errors, 1):
                logger.info(f"   {i}. {error}")

        # Calculate average capture time
        capture_times = [
            a["capture_time_ms"]
            for a in self.session_data["actions"]
            if a["capture_time_ms"] > 0
        ]
        if capture_times:
            avg_capture = sum(capture_times) / len(capture_times)
            logger.info(f"\n⏱️  Performance:")
            logger.info(f"   Avg Vision Capture: {avg_capture:.2f}ms")

            if avg_capture < 500:
                logger.info(f"   ✅ Vision meets NFR-001 (<500ms)")
            else:
                logger.info(f"   ❌ Vision exceeds NFR-001 (>500ms)")

        # Save session
        self.session_data["end_time"] = datetime.now().isoformat()
        self.session_data["summary"] = {
            "actions_executed": self.actions_executed,
            "actions_blocked": self.actions_blocked,
            "errors": len(self.errors),
            "success": self.actions_executed >= self.max_actions and len(self.errors) == 0,
        }

        session_file = (
            Path("data/sessions")
            / f"e2e_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        session_file.parent.mkdir(parents=True, exist_ok=True)

        with open(session_file, "w") as f:
            json.dump(self.session_data, f, indent=2)

        logger.info(f"\n💾 Session saved to: {session_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="End-to-end test for Cultist Simulator AI Agent"
    )
    parser.add_argument(
        "--actions",
        type=int,
        default=10,
        help="Number of actions to execute (default: 10)",
    )
    parser.add_argument(
        "--window",
        type=str,
        default="Cultist Simulator",
        help="Game window name (default: 'Cultist Simulator')",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Test without actually clicking"
    )
    parser.add_argument(
        "--test-mode", action="store_true", help="Use random actions (no trained model required)"
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed logging")

    args = parser.parse_args()

    # Create and run test
    runner = E2ETestRunner(
        window_name=args.window, 
        max_actions=args.actions, 
        dry_run=args.dry_run,
        test_mode=args.test_mode
    )

    success = runner.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
