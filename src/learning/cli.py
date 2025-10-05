#!/usr/bin/env python3
"""
Learning Library CLI

Provides command-line interface for knowledge base and metrics functions.
T104: Learning library CLI with JSON I/O.
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.learning import KnowledgeBase, MetricsTracker, StrategyManager

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Learning Library CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # Query KB
    kb_parser = subparsers.add_parser("query-kb", help="Query knowledge base")
    kb_parser.add_argument("key", help="Key to query")
    
    # Get metrics
    metrics_parser = subparsers.add_parser("get-metrics", help="Get metrics summary")
    
    # List strategies
    strategies_parser = subparsers.add_parser("list-strategies", help="List all strategies")
    
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--db", default="data/knowledge_base.db", help="Database path")
    
    args = parser.parse_args()
    
    try:
        if args.command == "query-kb":
            kb = KnowledgeBase(args.db)
            result = kb.get_mechanic(args.key)
            
            if args.json:
                print(json.dumps({"status": "success", "result": result}))
            else:
                print(f"✓ Result: {result}")
        
        elif args.command == "get-metrics":
            tracker = MetricsTracker()
            stats = tracker.get_aggregate_stats()
            
            if args.json:
                print(json.dumps({"status": "success", "metrics": stats}))
            else:
                print(f"✓ Metrics summary:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
        
        elif args.command == "list-strategies":
            manager = StrategyManager()
            strategies = manager.list_strategies()
            
            if args.json:
                print(json.dumps({
                    "status": "success",
                    "count": len(strategies),
                    "strategies": [s.name for s in strategies]
                }))
            else:
                print(f"✓ Found {len(strategies)} strategies:")
                for s in strategies:
                    print(f"  - {s.name}")
        
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
