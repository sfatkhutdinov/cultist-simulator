#!/usr/bin/env python3
"""
Safety Library CLI

Provides command-line interface for safety validation functions.
T079: Safety library CLI with JSON I/O.
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.safety import validate_action, is_within_bounds
from src.lib.types import ActionType, Action, Point
from datetime import datetime

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Safety Library CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate an action")
    validate_parser.add_argument("action_type", choices=["click", "drag", "key"])
    validate_parser.add_argument("params", nargs="+", help="Action parameters")
    
    # Bounds check
    bounds_parser = subparsers.add_parser("check-bounds", help="Check if point is within bounds")
    bounds_parser.add_argument("x", type=int)
    bounds_parser.add_argument("y", type=int)
    
    parser.add_argument("--json", action="store_true")
    
    args = parser.parse_args()
    
    try:
        if args.command == "validate":
            # Create action from params
            if args.action_type == "click":
                action = Action(
                    action_type=ActionType.CLICK,
                    parameters={"x": int(args.params[0]), "y": int(args.params[1])},
                    timestamp=datetime.now()
                )
            else:
                action = Action(action_type=ActionType.WAIT, parameters={}, timestamp=datetime.now())
            
            result = validate_action(action)
            
            if args.json:
                print(json.dumps({
                    "status": "success",
                    "valid": result.is_valid,
                    "reason": result.reason if hasattr(result, 'reason') else None
                }))
            else:
                print(f"✓ Action valid: {result.is_valid}")
        
        elif args.command == "check-bounds":
            point = Point(x=args.x, y=args.y)
            valid = is_within_bounds(point)
            
            if args.json:
                print(json.dumps({"status": "success", "within_bounds": valid}))
            else:
                print(f"✓ Point ({args.x}, {args.y}) within bounds: {valid}")
        
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
