#!/usr/bin/env python3
"""
NLP Library CLI

Provides command-line interface for text analysis functions.
T089: NLP library CLI with JSON I/O.
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.nlp import analyze_text, extract_goals, calculate_similarity


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="NLP Library CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text")
    analyze_parser.add_argument("text", help="Text to analyze")

    # Extract goals
    goals_parser = subparsers.add_parser(
        "extract-goals", help="Extract goals from text"
    )
    goals_parser.add_argument("text", help="Text to extract goals from")

    # Similarity
    similarity_parser = subparsers.add_parser(
        "similarity", help="Calculate text similarity"
    )
    similarity_parser.add_argument("text1", help="First text")
    similarity_parser.add_argument("text2", help="Second text")

    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    try:
        if args.command == "analyze":
            result = analyze_text(args.text)

            if args.json:
                print(
                    json.dumps(
                        {
                            "status": "success",
                            "entities": (
                                result.entities if hasattr(result, "entities") else []
                            ),
                            "sentiment": (
                                result.sentiment
                                if hasattr(result, "sentiment")
                                else None
                            ),
                        }
                    )
                )
            else:
                print(f"✓ Analysis complete")

        elif args.command == "extract-goals":
            goals = extract_goals(args.text)

            if args.json:
                print(json.dumps({"status": "success", "goals": goals}))
            else:
                print(f"✓ Found {len(goals)} goals")
                for goal in goals:
                    print(f"  - {goal}")

        elif args.command == "similarity":
            score = calculate_similarity(args.text1, args.text2)

            if args.json:
                print(json.dumps({"status": "success", "similarity": score}))
            else:
                print(f"✓ Similarity: {score:.3f}")

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
