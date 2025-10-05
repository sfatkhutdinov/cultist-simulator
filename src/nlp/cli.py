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

from src.nlp import analyze_text, extract_goals, find_similar_narratives


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
                            "text": result.text,
                            "embedding_dim": len(result.embedding),
                            "model": result.model_name,
                            "processing_time_ms": result.processing_time_ms,
                        }
                    )
                )
            else:
                print(f"✓ Analyzed text: {result.text[:50]}...")
                print(f"  Model: {result.model_name}")
                print(f"  Embedding dimension: {len(result.embedding)}")
                print(f"  Processing time: {result.processing_time_ms:.2f}ms")

        elif args.command == "extract-goals":
            goals = extract_goals(args.text)

            if args.json:
                print(json.dumps({"status": "success", "goals": goals}))
            else:
                print(f"✓ Found {len(goals)} goals")
                for goal in goals:
                    print(f"  - {goal}")

        elif args.command == "similarity":
            # Use analyze_text to get embeddings and calculate cosine similarity
            import numpy as np

            result1 = analyze_text(args.text1)
            result2 = analyze_text(args.text2)

            # Calculate cosine similarity
            emb1 = np.array(result1.embedding)
            emb2 = np.array(result2.embedding)
            score = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

            if args.json:
                print(json.dumps({"status": "success", "similarity": float(score)}))
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
