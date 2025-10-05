#!/usr/bin/env python3
"""
Vision Library CLI

Provides command-line interface for vision library functions.
T059: Vision library CLI with JSON I/O.
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vision import capture_game_state, detect_elements, extract_text_regions
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Vision Library CLI")
    parser.add_argument(
        "command", choices=["capture", "detect", "ocr"], help="Command to execute"
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument(
        "--window-name", default="Cultist Simulator", help="Game window name"
    )

    args = parser.parse_args()

    try:
        if args.command == "capture":
            state = capture_game_state(window_name=args.window_name)
            if args.json:
                print(
                    json.dumps(
                        {
                            "status": "success",
                            "elements_count": len(state.elements),
                            "text_regions_count": len(state.text_regions),
                            "timestamp": state.timestamp.isoformat(),
                        }
                    )
                )
            else:
                print(
                    f"✓ Captured game state: {len(state.elements)} elements, {len(state.text_regions)} text regions"
                )

        elif args.command == "detect":
            state = capture_game_state(window_name=args.window_name)
            elements = (
                detect_elements(state.screenshot)
                if state.screenshot is not None
                else []
            )
            if args.json:
                print(
                    json.dumps(
                        {
                            "status": "success",
                            "elements": [
                                {
                                    "type": e.element_type.value,
                                    "bounds": {
                                        "x": e.bounds.x,
                                        "y": e.bounds.y,
                                        "width": e.bounds.width,
                                        "height": e.bounds.height,
                                    },
                                }
                                for e in elements
                            ],
                        }
                    )
                )
            else:
                print(f"✓ Detected {len(elements)} elements")

        elif args.command == "ocr":
            state = capture_game_state(window_name=args.window_name)
            texts = (
                extract_text_regions(state.screenshot)
                if state.screenshot is not None
                else []
            )
            if args.json:
                print(
                    json.dumps(
                        {
                            "status": "success",
                            "texts": [
                                {"text": t.text, "confidence": t.confidence}
                                for t in texts
                            ],
                        }
                    )
                )
            else:
                print(f"✓ Extracted {len(texts)} text regions")
                for t in texts[:5]:
                    print(f"  - {t.text} ({t.confidence:.2f})")

    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        else:
            print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
