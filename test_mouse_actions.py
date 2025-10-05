#!/usr/bin/env python3
"""
Quick test to verify mouse automation works with the actual game window.
This will move the mouse and click a few times to demonstrate the automation is functional.
"""

from src.lib.types import Point, Rect, MouseButton, ActionType, Action
from src.automation import simulate_click, simulate_drag, wait
from src.automation.window_manager import get_active_window_bounds
import time

def main():
    window_name = "Cultist Simulator"
    
    print(f"🎮 Testing mouse automation with {window_name}")
    print("=" * 60)
    
    # Get the game window bounds
    try:
        bounds = get_active_window_bounds(window_name)
        print(f"✅ Found window: {bounds}")
    except Exception as e:
        print(f"❌ Window not found: {e}")
        print("Make sure Cultist Simulator is running and focused!")
        return
    
    # Calculate center of window
    center_x = bounds.x + bounds.width // 2
    center_y = bounds.y + bounds.height // 2
    center = Point(x=center_x, y=center_y)
    
    # Test 1: Move to center and click
    print(f"\n1️⃣  Clicking center of window at ({center_x}, {center_y})")
    try:
        simulate_click(center, "left", bounds)
        print("✅ Click successful!")
    except Exception as e:
        print(f"❌ Click failed: {e}")
    
    wait(1000)  # Wait 1 second
    
    # Test 2: Click top-left quadrant
    top_left = Point(x=bounds.x + bounds.width // 4, y=bounds.y + bounds.height // 4)
    print(f"\n2️⃣  Clicking top-left quadrant at ({top_left.x}, {top_left.y})")
    try:
        simulate_click(top_left, "left", bounds)
        print("✅ Click successful!")
    except Exception as e:
        print(f"❌ Click failed: {e}")
    
    wait(1000)
    
    # Test 3: Click bottom-right quadrant
    bottom_right = Point(x=bounds.x + 3 * bounds.width // 4, y=bounds.y + 3 * bounds.height // 4)
    print(f"\n3️⃣  Clicking bottom-right quadrant at ({bottom_right.x}, {bottom_right.y})")
    try:
        simulate_click(bottom_right, "left", bounds)
        print("✅ Click successful!")
    except Exception as e:
        print(f"❌ Click failed: {e}")
    
    wait(1000)
    
    # Test 4: Drag from left to right
    drag_start = Point(x=bounds.x + bounds.width // 3, y=center_y)
    drag_end = Point(x=bounds.x + 2 * bounds.width // 3, y=center_y)
    print(f"\n4️⃣  Dragging from ({drag_start.x}, {drag_start.y}) to ({drag_end.x}, {drag_end.y})")
    try:
        simulate_drag(drag_start, drag_end, 500, bounds)  # 500ms drag
        print("✅ Drag successful!")
    except Exception as e:
        print(f"❌ Drag failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Mouse automation test complete!")
    print("\nYou should have seen:")
    print("  - Mouse moving to different positions")
    print("  - Clicks at 3 different locations")
    print("  - A drag motion across the window")

if __name__ == "__main__":
    main()
