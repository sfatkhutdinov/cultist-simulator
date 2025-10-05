#!/usr/bin/env python3
"""
Adversarial Safety Testing - T135

Tests safety constraints with adversarial inputs attempting to bypass
all safety mechanisms. This is CRITICAL for production readiness.

SUCCESS CRITERIA:
- 100% of adversarial attacks must be blocked
- No actions execute outside window bounds
- No blacklisted keys are pressed
- Rate limiting cannot be bypassed
- Window focus requirement cannot be bypassed

ATTACK VECTORS:
1. Out-of-bounds coordinates
2. Blacklisted key combinations
3. Rapid-fire actions (rate limit bypass)
4. Window unfocused attacks
5. Invalid action types
6. Malformed inputs
7. SQL injection attempts (knowledge base)
8. Path traversal attempts
9. Resource exhaustion
10. Timing attacks
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.safety import validate_action
from src.automation import simulate_click, simulate_key_press
from src.lib.types import ActionType, Point, Rect
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class AdversarialTester:
    """Adversarial safety testing framework."""

    def __init__(self):
        self.attacks_attempted = 0
        self.attacks_blocked = 0
        self.attacks_succeeded = 0
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "attacks": [],
            "summary": {},
        }
        self.window_bounds = Rect(0, 0, 1920, 1080)

    def log_attack(self, name: str, blocked: bool, reason: str = ""):
        """Log attack result."""
        self.attacks_attempted += 1
        if blocked:
            self.attacks_blocked += 1
            status = "✅ BLOCKED"
        else:
            self.attacks_succeeded += 1
            status = "❌ SUCCESS (SECURITY ISSUE!)"

        result = {
            "attack": name,
            "blocked": blocked,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }
        self.results["attacks"].append(result)

        logger.info(f"{status}: {name}")
        if not blocked:
            logger.error(f"SECURITY BREACH: {name} - {reason}")

    def test_out_of_bounds_attacks(self):
        """Test 1: Out-of-bounds coordinate attacks."""
        print("\n" + "=" * 60)
        print("TEST 1: Out-of-Bounds Attacks")
        print("=" * 60)

        attacks = [
            ("Negative X", Point(-100, 500)),
            ("Negative Y", Point(500, -100)),
            ("X beyond bounds", Point(3000, 500)),
            ("Y beyond bounds", Point(500, 2000)),
            ("Both negative", Point(-500, -500)),
            ("Both beyond", Point(5000, 5000)),
            ("Integer overflow", Point(2147483647, 500)),
        ]

        for name, point in attacks:
            action = {"action_type": ActionType.CLICK, "point": point}
            context = {"window_bounds": self.window_bounds, "window_focused": True}

            try:
                validation = validate_action(action, context)
                blocked = not validation.is_allowed
                reason = (
                    validation.blocked_reason
                    if hasattr(validation, "blocked_reason")
                    else "Not specified"
                )
                self.log_attack(f"OOB: {name}", blocked, reason)
            except Exception as e:
                # Exceptions are also acceptable (crash prevention)
                self.log_attack(f"OOB: {name}", True, f"Exception: {e}")

        # Test float injection separately - create Point-like object with float coords
        class FakePoint:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __str__(self):
                return f"FakePoint({self.x}, {self.y})"

        float_point = FakePoint(100.5, 200.7)
        action = {"action_type": ActionType.CLICK, "point": float_point}
        context = {"window_bounds": self.window_bounds, "window_focused": True}

        try:
            validation = validate_action(action, context)
            # Should be blocked because coords are not integers
            blocked = not validation.is_allowed
            reason = (
                validation.blocked_reason
                if hasattr(validation, "blocked_reason")
                else "Not specified"
            )
            self.log_attack("OOB: Float injection", blocked, reason)
        except Exception as e:
            self.log_attack("OOB: Float injection", True, f"Exception: {e}")

    def test_blacklist_attacks(self):
        """Test 2: Blacklisted key combination attacks."""
        print("\n" + "=" * 60)
        print("TEST 2: Blacklisted Key Attacks")
        print("=" * 60)

        dangerous_keys = [
            ("Quit application", "q", ["cmd"]),
            ("Close window", "w", ["cmd"]),
            ("Force quit", "q", ["cmd", "option"]),
            ("Switch apps", "tab", ["cmd"]),
            ("Task manager (Win)", "escape", ["ctrl", "shift"]),
            ("Alt-F4 (Win)", "f4", ["alt"]),
            ("Multiple modifiers", "q", ["cmd", "shift", "option"]),
            ("Case variation", "Q", ["cmd"]),  # Should normalize
        ]

        for name, key, modifiers in dangerous_keys:
            action = {
                "action_type": ActionType.KEY_PRESS,
                "key": key,
                "modifiers": modifiers,
            }
            context = {"window_bounds": self.window_bounds, "window_focused": True}

            try:
                validation = validate_action(action, context)
                blocked = not validation.is_allowed
                reason = (
                    validation.blocked_reason
                    if hasattr(validation, "blocked_reason")
                    else "Not specified"
                )
                self.log_attack(f"Blacklist: {name}", blocked, reason)
            except Exception as e:
                self.log_attack(f"Blacklist: {name}", True, f"Exception: {e}")

    def test_rate_limit_attacks(self):
        """Test 3: Rate limiting bypass attempts."""
        print("\n" + "=" * 60)
        print("TEST 3: Rate Limiting Attacks")
        print("=" * 60)

        # Attempt rapid-fire actions with action history tracking
        action = {"action_type": ActionType.CLICK, "point": Point(100, 100)}

        # Simulate action history (recent actions within last second)
        current_time = time.time()
        action_history = []

        # Try to exceed rate limit (max 10 actions/sec)
        attempts = 50
        blocked_count = 0
        start_time = time.time()

        for i in range(attempts):
            # Build context with growing action history
            context = {
                "window_bounds": self.window_bounds,
                "window_focused": True,
                "recent_actions": action_history.copy(),  # Copy current history
                "max_actions_per_second": 10,
            }

            try:
                validation = validate_action(action, context)
                if not validation.is_allowed:
                    blocked_count += 1
                else:
                    # Add to history if allowed
                    action_history.append(
                        {"timestamp": current_time, "action_type": ActionType.CLICK}
                    )
            except Exception:
                blocked_count += 1

        elapsed = time.time() - start_time
        rate = attempts / elapsed

        # If rate limiting works, many should be blocked (>=40 out of 50)
        if blocked_count >= 40:  # At least 40 blocked
            self.log_attack(
                f"Rate limit bypass ({rate:.1f} req/s)",
                True,
                f"{blocked_count}/{attempts} blocked",
            )
        else:
            self.log_attack(
                f"Rate limit bypass ({rate:.1f} req/s)",
                False,
                f"Only {blocked_count}/{attempts} blocked - insufficient rate limiting",
            )

    def test_window_focus_attacks(self):
        """Test 4: Window focus bypass attempts."""
        print("\n" + "=" * 60)
        print("TEST 4: Window Focus Attacks")
        print("=" * 60)

        action = {"action_type": ActionType.CLICK, "point": Point(100, 100)}

        # Try with window unfocused
        context_unfocused = {
            "window_bounds": self.window_bounds,
            "window_focused": False,
        }

        try:
            validation = validate_action(action, context_unfocused)
            blocked = not validation.is_allowed
            reason = (
                validation.blocked_reason
                if hasattr(validation, "blocked_reason")
                else "Not specified"
            )
            self.log_attack("Unfocused window click", blocked, reason)
        except Exception as e:
            self.log_attack("Unfocused window click", True, f"Exception: {e}")

        # Try with missing focus field
        context_no_focus = {"window_bounds": self.window_bounds}

        try:
            validation = validate_action(action, context_no_focus)
            # Should either block or assume unfocused
            blocked = not validation.is_allowed
            self.log_attack("Missing focus field", blocked, "Handled gracefully")
        except Exception as e:
            self.log_attack("Missing focus field", True, f"Exception: {e}")

    def test_invalid_action_types(self):
        """Test 5: Invalid action type attacks."""
        print("\n" + "=" * 60)
        print("TEST 5: Invalid Action Type Attacks")
        print("=" * 60)

        invalid_actions = [
            ("None action type", None),
            ("Invalid string", "INVALID_ACTION"),
            ("SQL injection", "'; DROP TABLE actions; --"),
            ("XSS attempt", "<script>alert('xss')</script>"),
            ("Path traversal", "../../etc/passwd"),
        ]

        for name, action_type in invalid_actions:
            action = {"action_type": action_type, "point": Point(100, 100)}
            context = {"window_bounds": self.window_bounds, "window_focused": True}

            try:
                validation = validate_action(action, context)
                # Should reject invalid types
                blocked = not validation.is_allowed
                self.log_attack(f"Invalid type: {name}", blocked)
            except Exception as e:
                # Exception is acceptable for invalid input
                self.log_attack(f"Invalid type: {name}", True, f"Exception: {e}")

    def test_malformed_inputs(self):
        """Test 6: Malformed input attacks."""
        print("\n" + "=" * 60)
        print("TEST 6: Malformed Input Attacks")
        print("=" * 60)

        malformed = [
            ("Empty action", {}),
            ("Missing point", {"action_type": ActionType.CLICK}),
            ("Point as string", {"action_type": ActionType.CLICK, "point": "100,100"}),
            ("None point", {"action_type": ActionType.CLICK, "point": None}),
            (
                "Invalid context",
                {"action_type": ActionType.CLICK, "point": Point(100, 100)},
            ),
        ]

        for name, action in malformed:
            context = (
                {"window_bounds": self.window_bounds, "window_focused": True}
                if "Invalid context" not in name
                else {}
            )

            try:
                validation = validate_action(action, context)
                blocked = not validation.is_allowed
                self.log_attack(f"Malformed: {name}", blocked)
            except Exception as e:
                # Exception handling is acceptable
                self.log_attack(f"Malformed: {name}", True, f"Exception: {e}")

    def test_resource_exhaustion(self):
        """Test 7: Resource exhaustion attacks."""
        print("\n" + "=" * 60)
        print("TEST 7: Resource Exhaustion Attacks")
        print("=" * 60)

        # Try massive coordinates
        action = {"action_type": ActionType.CLICK, "point": Point(999999999, 999999999)}
        context = {"window_bounds": self.window_bounds, "window_focused": True}

        try:
            start = time.time()
            validation = validate_action(action, context)
            elapsed = time.time() - start

            # Should complete quickly even with huge values
            if elapsed < 0.1:  # < 100ms
                blocked = not validation.is_allowed
                self.log_attack(
                    "Huge coordinates", blocked, f"Validated in {elapsed*1000:.2f}ms"
                )
            else:
                self.log_attack(
                    "Huge coordinates",
                    False,
                    f"Slow validation ({elapsed*1000:.2f}ms) - DoS risk",
                )
        except Exception as e:
            self.log_attack("Huge coordinates", True, f"Exception: {e}")

    def test_timing_attacks(self):
        """Test 8: Timing-based attacks."""
        print("\n" + "=" * 60)
        print("TEST 8: Timing Attack Resistance")
        print("=" * 60)

        # Validation timing should be consistent
        action_valid = {"action_type": ActionType.CLICK, "point": Point(100, 100)}
        action_invalid = {"action_type": ActionType.CLICK, "point": Point(-100, -100)}
        context = {"window_bounds": self.window_bounds, "window_focused": True}

        # Time valid actions
        valid_times = []
        for _ in range(10):
            start = time.time()
            validate_action(action_valid, context)
            valid_times.append(time.time() - start)

        # Time invalid actions
        invalid_times = []
        for _ in range(10):
            start = time.time()
            validate_action(action_invalid, context)
            invalid_times.append(time.time() - start)

        avg_valid = sum(valid_times) / len(valid_times)
        avg_invalid = sum(invalid_times) / len(invalid_times)
        difference = abs(avg_valid - avg_invalid)

        # Timing should be similar (< 10ms difference)
        if difference < 0.01:  # < 10ms
            self.log_attack(
                "Timing attack resistance",
                True,
                f"Timing difference: {difference*1000:.2f}ms",
            )
        else:
            self.log_attack(
                "Timing attack resistance",
                False,
                f"Timing leak: {difference*1000:.2f}ms difference",
            )

    def generate_report(self):
        """Generate comprehensive security report."""
        print("\n" + "=" * 60)
        print("ADVERSARIAL TESTING REPORT")
        print("=" * 60)

        print(f"\n📊 Statistics:")
        print(f"   Total Attacks: {self.attacks_attempted}")
        print(f"   Blocked:       {self.attacks_blocked}")
        print(f"   Succeeded:     {self.attacks_succeeded}")

        block_rate = (
            (self.attacks_blocked / self.attacks_attempted * 100)
            if self.attacks_attempted > 0
            else 0
        )
        print(f"   Block Rate:    {block_rate:.1f}%")

        if self.attacks_succeeded == 0:
            print("\n✅ ALL ATTACKS BLOCKED - SECURITY PASSED")
            passed = True
        else:
            print(f"\n❌ {self.attacks_succeeded} ATTACKS SUCCEEDED - SECURITY FAILED")
            print("\nFailed attacks:")
            for attack in self.results["attacks"]:
                if not attack["blocked"]:
                    print(
                        f"   • {attack['attack']}: {attack.get('reason', 'No reason')}"
                    )
            passed = False

        # Save report
        self.results["summary"] = {
            "total_attacks": self.attacks_attempted,
            "blocked": self.attacks_blocked,
            "succeeded": self.attacks_succeeded,
            "block_rate": block_rate,
            "passed": passed,
        }

        report_file = Path("data/security_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Report saved to: {report_file}")

        return passed

    def run_all_tests(self):
        """Run complete adversarial test suite."""
        print("\n" + "=" * 60)
        print("ADVERSARIAL SAFETY TESTING")
        print("=" * 60)
        print("\nTesting security constraints with adversarial inputs...")
        print("CRITICAL: 100% of attacks must be blocked for production readiness\n")

        self.test_out_of_bounds_attacks()
        self.test_blacklist_attacks()
        self.test_rate_limit_attacks()
        self.test_window_focus_attacks()
        self.test_invalid_action_types()
        self.test_malformed_inputs()
        self.test_resource_exhaustion()
        self.test_timing_attacks()

        passed = self.generate_report()

        print("\n" + "=" * 60)
        if passed:
            print("✅ ADVERSARIAL TESTING PASSED")
        else:
            print("❌ ADVERSARIAL TESTING FAILED")
        print("=" * 60 + "\n")

        return passed


def main():
    """Main entry point."""
    tester = AdversarialTester()
    passed = tester.run_all_tests()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
