#!/usr/bin/env python3
"""
Random Exploration Test - Demonstrates Full Automation Capabilities

This script performs random actions on the Cultist Simulator window to demonstrate
that all automation features (click, drag, keyboard) are working properly.

This is NOT intelligent gameplay - it's just random exploration to test the system.
"""

import random
import time
from src.lib.types import Point, Rect, ActionType
from src.automation import simulate_click, simulate_drag, simulate_key_press, wait
from src.automation.window_manager import get_active_window_bounds, is_window_active
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


def random_point_in_bounds(bounds: Rect) -> Point:
    """Generate a random point within window bounds."""
    # Stay away from edges (10% margin)
    margin_x = int(bounds.width * 0.1)
    margin_y = int(bounds.height * 0.1)
    
    x = random.randint(bounds.x + margin_x, bounds.x + bounds.width - margin_x)
    y = random.randint(bounds.y + margin_y, bounds.y + bounds.height - margin_y)
    
    return Point(x=x, y=y)


def perform_random_click(bounds: Rect):
    """Perform a random click somewhere in the window."""
    point = random_point_in_bounds(bounds)
    button = random.choice(["left", "left", "left", "right"])  # Favor left clicks
    
    print(f"  🖱️  Clicking {button} button at ({point.x}, {point.y})")
    try:
        simulate_click(point, button, bounds)
        logger.info(f"Random click executed", point=point, button=button)
    except Exception as e:
        logger.error(f"Click failed", error=str(e))
        print(f"    ❌ Failed: {e}")


def perform_random_drag(bounds: Rect):
    """Perform a random drag motion."""
    start = random_point_in_bounds(bounds)
    end = random_point_in_bounds(bounds)
    duration = random.randint(300, 800)
    
    print(f"  ↔️  Dragging from ({start.x}, {start.y}) to ({end.x}, {end.y}) over {duration}ms")
    try:
        simulate_drag(start, end, duration, bounds)
        logger.info(f"Random drag executed", start=start, end=end, duration=duration)
    except Exception as e:
        logger.error(f"Drag failed", error=str(e))
        print(f"    ❌ Failed: {e}")


def perform_random_keypress(bounds: Rect):
    """Perform a safe random keypress."""
    # Only safe keys - no Cmd combinations or dangerous keys
    safe_keys = [
        "space",      # Common game action
        "tab",        # UI navigation
        "escape",     # Menu
        "return",     # Confirm
        "1", "2", "3", "4", "5",  # Number keys
        "a", "s", "d", "w",  # Movement keys
    ]
    
    key = random.choice(safe_keys)
    
    print(f"  ⌨️  Pressing key: {key}")
    try:
        simulate_key_press(key, [], bounds)
        logger.info(f"Random keypress executed", key=key)
    except Exception as e:
        logger.error(f"Keypress failed", error=str(e))
        print(f"    ❌ Failed: {e}")


def main():
    window_name = "Cultist Simulator"
    num_actions = 15  # Number of random actions to perform
    
    print("🎲 RANDOM EXPLORATION TEST")
    print("=" * 70)
    print(f"Window: {window_name}")
    print(f"Actions: {num_actions}")
    print("=" * 70)
    print()
    print("⚠️  NOTE: This performs RANDOM actions - not intelligent gameplay!")
    print("   The mouse will move around and click/drag randomly.")
    print()
    input("Press ENTER to start (make sure the game window is visible)... ")
    print()
    
    # Get window bounds
    try:
        bounds = get_active_window_bounds(window_name)
        print(f"✅ Found window: {bounds}")
        print()
    except Exception as e:
        print(f"❌ Window not found: {e}")
        print("   Make sure Cultist Simulator is running!")
        return
    
    # Check if window is focused
    if not is_window_active(window_name):
        print("⚠️  Warning: Window is not focused. Click on the game window first!")
        input("Press ENTER after focusing the game window... ")
        print()
    
    # Perform random actions
    action_types = [
        ("click", 5),     # Weight: 5
        ("drag", 2),      # Weight: 2
        ("keypress", 3),  # Weight: 3
    ]
    
    # Create weighted list
    weighted_actions = []
    for action_type, weight in action_types:
        weighted_actions.extend([action_type] * weight)
    
    for i in range(num_actions):
        print(f"Action {i+1}/{num_actions}:")
        
        # Check if window is still focused
        if not is_window_active(window_name):
            print("  ⚠️  Window lost focus - pausing...")
            input("  Press ENTER after focusing the game window to continue... ")
        
        # Choose and perform random action
        action_type = random.choice(weighted_actions)
        
        if action_type == "click":
            perform_random_click(bounds)
        elif action_type == "drag":
            perform_random_drag(bounds)
        elif action_type == "keypress":
            perform_random_keypress(bounds)
        
        # Wait between actions
        pause = random.uniform(0.5, 1.5)
        print(f"  ⏸️  Waiting {pause:.1f}s...")
        wait(int(pause * 1000))
        print()
    
    print("=" * 70)
    print("✅ RANDOM EXPLORATION COMPLETE!")
    print()
    print("Summary:")
    print(f"  - Performed {num_actions} random actions")
    print(f"  - All actions were safety-validated")
    print(f"  - Window bounds were respected")
    print()
    print("You should have seen:")
    print("  ✓ Mouse moving to random positions")
    print("  ✓ Random clicks (left and right)")
    print("  ✓ Random drag motions")
    print("  ✓ Random safe keypresses")
    print()
    print("Check the logs for detailed action information!")


if __name__ == "__main__":
    main()
