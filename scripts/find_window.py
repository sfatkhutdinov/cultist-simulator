#!/usr/bin/env python3
"""
Window Finder - Helper script to test window detection

This script attempts to find and connect to the Cultist Simulator window.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.vision import get_window_bounds


def main():
    print("=" * 60)
    print("WINDOW DETECTION TEST")
    print("=" * 60)

    # Common window name variations
    window_names = [
        "Cultist Simulator",
        "Cultist Simulator - Unity",
        "Unity Player",
        "Cultist",
    ]

    print("\nTrying common window names...\n")

    found = []

    for window_name in window_names:
        try:
            print(f"Testing: '{window_name}'...")
            bounds = get_window_bounds(window_name)
            if bounds:
                print(f"   ✅ FOUND: {bounds}")
                found.append((window_name, bounds))
            else:
                print(f"   ❌ Not found")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    if found:
        print("SUCCESS - Window(s) detected:")
        print("=" * 60)
        for name, bounds in found:
            print(f"\nWindow: '{name}'")
            print(f"Bounds: {bounds}")
            print(f"\nTo run E2E test:")
            print(f'   python3 scripts/test_e2e.py --window "{name}"')
    else:
        print("NO WINDOWS FOUND")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Make sure Cultist Simulator is running")
        print("2. Check the game window title in the menu bar")
        print("3. Grant Screen Recording permissions:")
        print("   System Settings > Privacy & Security > Screen Recording")
        print("4. Try running with the exact window title you see")
        print("\nExample:")
        print('   python3 scripts/test_e2e.py --window "Your Window Title"')


if __name__ == "__main__":
    main()
