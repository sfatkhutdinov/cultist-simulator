#!/usr/bin/env python3
"""
Orchestrator CLI - Command-line interface for autonomous agent.

Commands:
- run: Run a single episode
- train: Train agent across multiple episodes
- metrics: Show agent performance metrics
- strategy: Display agent's current strategy

T113: Main orchestrator CLI.
"""

import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrator import (
    run_episode,
    train_agent,
    get_agent_metrics,
    articulate_strategy,
)
from src.orchestrator.tensorboard_vscode import (
    launch_tensorboard_in_vscode,
    create_tensorboard_notice,
)
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


def cmd_run(args):
    """Run a single episode."""
    print(f"Starting episode for agent: {args.agent_id}")
    print(f"Window: {args.window}")
    print(f"Max actions: {args.max_actions}\n")

    try:
        session = run_episode(
            agent_id=args.agent_id,
            window_name=args.window,
            max_actions=args.max_actions,
            max_duration_seconds=args.max_duration,
        )

        print(f"\n{'='*60}")
        print(f"Episode Complete!")
        print(f"{'='*60}")
        print(f"Session ID: {session.session_id}")
        print(f"Total Actions: {session.total_actions}")
        print(
            f"Duration: {session.duration_seconds:.1f}s"
            if session.duration_seconds
            else "Duration: N/A"
        )
        print(
            f"End Condition: {session.end_condition.value if session.end_condition else 'N/A'}"
        )
        print(f"{'='*60}\n")

        if args.output:
            # Save session to JSON
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            session_data = {
                "session_id": session.session_id,
                "agent_id": session.agent_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "total_actions": session.total_actions,
                "total_reward": session.total_reward,
                "end_condition": (
                    session.end_condition.value if session.end_condition else None
                ),
                "duration_seconds": session.duration_seconds,
            }

            with open(output_path, "w") as f:
                json.dump(session_data, f, indent=2)

            print(f"Session data saved to: {output_path}")

        return 0

    except KeyboardInterrupt:
        print("\n\nEpisode interrupted by user.")
        return 130

    except Exception as e:
        print(f"\nError running episode: {e}", file=sys.stderr)
        logger.error("cli_run_error", error=str(e), exc_info=True)
        return 1


def cmd_train(args):
    """Train agent across multiple episodes."""
    print(f"Training agent: {args.agent_id}")
    print(f"Episodes: {args.episodes}")
    print(f"Window: {args.window}")
    print(f"Max actions per episode: {args.max_actions}")
    print(f"Checkpoint every {args.checkpoint} episodes\n")

    # Launch TensorBoard in VS Code if requested
    tensorboard_dir = Path(__file__).parent.parent.parent / "data" / "tensorboard"

    if not args.no_tensorboard:
        print("🚀 Launching TensorBoard in VS Code...")
        launched = launch_tensorboard_in_vscode(str(tensorboard_dir))

        if not launched:
            # Show manual instructions if auto-launch failed
            print(create_tensorboard_notice(str(tensorboard_dir)))

    try:
        sessions = train_agent(
            agent_id=args.agent_id,
            num_episodes=args.episodes,
            window_name=args.window,
            max_actions_per_episode=args.max_actions,
            max_episode_duration=args.max_duration,
            checkpoint_interval=args.checkpoint,
        )

        print(f"\n{'='*60}")
        print(f"Training Complete!")
        print(f"{'='*60}")
        print(f"Episodes: {len(sessions)}")
        print(f"Total Actions: {sum(s.total_actions for s in sessions)}")
        print(
            f"Average Actions per Episode: {sum(s.total_actions for s in sessions) / len(sessions):.1f}"
        )
        print(f"{'='*60}\n")

        # Show final metrics
        metrics = get_agent_metrics(args.agent_id)
        print("Final Metrics:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")

        return 0

    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
        return 130

    except Exception as e:
        print(f"\nError during training: {e}", file=sys.stderr)
        logger.error("cli_train_error", error=str(e), exc_info=True)
        return 1


def cmd_metrics(args):
    """Show agent metrics."""
    metrics = get_agent_metrics(args.agent_id)

    if "error" in metrics:
        print(f"Error: {metrics['error']}")
        return 1

    print(f"\nAgent Metrics: {args.agent_id}")
    print(f"{'='*60}")

    for key, value in metrics.items():
        if isinstance(value, float):
            if "rate" in key:
                print(f"{key:30s}: {value:6.1%}")
            else:
                print(f"{key:30s}: {value:6.2f}")
        else:
            print(f"{key:30s}: {value:6}")

    print(f"{'='*60}\n")

    if args.output:
        # Save metrics to JSON
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(metrics, f, indent=2)

        print(f"Metrics saved to: {output_path}")

    return 0


def cmd_strategy(args):
    """Display agent strategy."""
    strategy = articulate_strategy(args.agent_id)
    print(strategy)
    print()

    if args.output:
        # Save strategy to text file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(strategy)

        print(f"Strategy saved to: {output_path}")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cultist Simulator Autonomous AI Agent - Orchestrator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a single episode
  %(prog)s run --agent-id my_agent --max-actions 100

  # Train for 50 episodes
  %(prog)s train --episodes 50 --checkpoint 10

  # View metrics
  %(prog)s metrics --agent-id my_agent

  # View strategy
  %(prog)s strategy --agent-id my_agent
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a single episode")
    run_parser.add_argument("--agent-id", default="agent_001", help="Agent identifier")
    run_parser.add_argument(
        "--window", default="Cultist Simulator", help="Game window name"
    )
    run_parser.add_argument(
        "--max-actions", type=int, default=1000, help="Maximum actions per episode"
    )
    run_parser.add_argument(
        "--max-duration",
        type=float,
        default=None,
        help="Maximum episode duration (seconds)",
    )
    run_parser.add_argument("--output", "-o", help="Save session data to JSON file")
    run_parser.set_defaults(func=cmd_run)

    # Train command
    train_parser = subparsers.add_parser(
        "train", help="Train agent across multiple episodes"
    )
    train_parser.add_argument(
        "--agent-id", default="agent_001", help="Agent identifier"
    )
    train_parser.add_argument(
        "--episodes", "-n", type=int, default=100, help="Number of episodes"
    )
    train_parser.add_argument(
        "--window", default="Cultist Simulator", help="Game window name"
    )
    train_parser.add_argument(
        "--max-actions", type=int, default=1000, help="Max actions per episode"
    )
    train_parser.add_argument(
        "--max-duration",
        type=float,
        default=300.0,
        help="Max duration per episode (seconds)",
    )
    train_parser.add_argument(
        "--checkpoint", type=int, default=10, help="Checkpoint interval (episodes)"
    )
    train_parser.add_argument(
        "--no-tensorboard",
        action="store_true",
        help="Disable automatic TensorBoard launch",
    )
    train_parser.set_defaults(func=cmd_train)

    # Metrics command
    metrics_parser = subparsers.add_parser(
        "metrics", help="Show agent performance metrics"
    )
    metrics_parser.add_argument(
        "--agent-id", default="agent_001", help="Agent identifier"
    )
    metrics_parser.add_argument("--output", "-o", help="Save metrics to JSON file")
    metrics_parser.set_defaults(func=cmd_metrics)

    # Strategy command
    strategy_parser = subparsers.add_parser("strategy", help="Display agent strategy")
    strategy_parser.add_argument(
        "--agent-id", default="agent_001", help="Agent identifier"
    )
    strategy_parser.add_argument("--output", "-o", help="Save strategy to text file")
    strategy_parser.set_defaults(func=cmd_strategy)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
