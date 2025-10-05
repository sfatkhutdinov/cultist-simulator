#!/usr/bin/env python3
"""
Automation Library CLI

Provides command-line interface for automation functions.
T070: Automation library CLI with JSON I/O.
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.automation import simulate_click, simulate_drag, simulate_key_press
from src.lib.types import Point, ActionType, Action
from datetime import datetime

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Automation Library CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Click command
    click_parser = subparsers.add_parser("click", help="Simulate mouse click")
    click_parser.add_argument("x", type=int, help="X coordinate")
    click_parser.add_argument("y", type=int, help="Y coordinate")
    click_parser.add_argument("--button", default="left", choices=["left", "right", "middle"])
    
    # Drag command
    drag_parser = subparsers.add_parser("drag", help="Simulate mouse drag")
    drag_parser.add_argument("x1", type=int, help="Start X")
    drag_parser.add_argument("y1", type=int, help="Start Y")
    drag_parser.add_argument("x2", type=int, help="End X")
    drag_parser.add_argument("y2", type=int, help="End Y")
    
    # Key command
    key_parser = subparsers.add_parser("key", help="Simulate key press")
    key_parser.add_argument("key", help="Key to press")
    
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    args = parser.parse_args()
    
    try:
        if args.command == "click":
            action = Action(
                action_type=ActionType.CLICK,
                parameters={"x": args.x, "y": args.y, "button": args.button},
                timestamp=datetime.now()
            )
            result = simulate_click(args.x, args.y, button=args.button)
            
            if args.json:
                print(json.dumps({"status": "success", "action": "click", "x": args.x, "y": args.y}))
            else:
                print(f"✓ Clicked at ({args.x}, {args.y})")
        
        elif args.command == "drag":
            start = Point(x=args.x1, y=args.y1)
            end = Point(x=args.x2, y=args.y2)
            result = simulate_drag(start, end)
            
            if args.json:
                print(json.dumps({
                    "status": "success",
                    "action": "drag",
                    "start": {"x": args.x1, "y": args.y1},
                    "end": {"x": args.x2, "y": args.y2}
                }))
            else:
                print(f"✓ Dragged from ({args.x1}, {args.y1}) to ({args.x2}, {args.y2})")
        
        elif args.command == "key":
            result = simulate_key_press(args.key)
            
            if args.json:
                print(json.dumps({"status": "success", "action": "key_press", "key": args.key}))
            else:
                print(f"✓ Pressed key: {args.key}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        else:
            print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
