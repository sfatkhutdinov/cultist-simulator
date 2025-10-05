"""
Performance Metrics Module

Tracks multi-dimensional performance metrics for the RL agent.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.lib.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceMetric:
    """
    Multi-dimensional performance tracking.
    T102, T103: Performance metric tracking system with survival time,
    win rate, resources, and unique endings.
    """

    session_id: str
    timestamp: datetime

    # Core metrics
    survival_time_seconds: float = 0.0
    game_result: str = "loss"  # win, loss, crash

    # Resource metrics
    final_resources: Dict[str, float] = field(default_factory=dict)
    max_resources_achieved: Dict[str, float] = field(default_factory=dict)

    # Discovery metrics
    unique_ending_id: Optional[str] = None
    cards_discovered: int = 0
    mechanics_learned: int = 0

    # Performance indicators
    actions_taken: int = 0
    errors_encountered: int = 0
    loops_detected: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "survival_time_seconds": self.survival_time_seconds,
            "game_result": self.game_result,
            "final_resources": self.final_resources,
            "max_resources_achieved": self.max_resources_achieved,
            "unique_ending_id": self.unique_ending_id,
            "cards_discovered": self.cards_discovered,
            "mechanics_learned": self.mechanics_learned,
            "actions_taken": self.actions_taken,
            "errors_encountered": self.errors_encountered,
            "loops_detected": self.loops_detected,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceMetric":
        """Deserialize from dictionary."""
        return cls(
            session_id=data["session_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            survival_time_seconds=data.get("survival_time_seconds", 0.0),
            game_result=data.get("game_result", "loss"),
            final_resources=data.get("final_resources", {}),
            max_resources_achieved=data.get("max_resources_achieved", {}),
            unique_ending_id=data.get("unique_ending_id"),
            cards_discovered=data.get("cards_discovered", 0),
            mechanics_learned=data.get("mechanics_learned", 0),
            actions_taken=data.get("actions_taken", 0),
            errors_encountered=data.get("errors_encountered", 0),
            loops_detected=data.get("loops_detected", 0),
            metadata=data.get("metadata", {}),
        )


class MetricsTracker:
    """
    Tracks and aggregates performance metrics across sessions.
    """

    def __init__(self, storage_path: str = "data/metrics.json"):
        """Initialize metrics tracker."""
        self.storage_path = storage_path
        self.metrics: List[PerformanceMetric] = []
        self._load_metrics()

    def _load_metrics(self) -> None:
        """Load metrics from disk."""
        import os

        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for metric_data in data.get("metrics", []):
                        metric = PerformanceMetric.from_dict(metric_data)
                        self.metrics.append(metric)
                logger.info(f"Loaded {len(self.metrics)} metrics")
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")

    def _save_metrics(self) -> None:
        """Save metrics to disk."""
        import os

        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            data = {"metrics": [m.to_dict() for m in self.metrics]}
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.metrics)} metrics")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def record_metric(self, metric: PerformanceMetric) -> None:
        """Record a new performance metric."""
        self.metrics.append(metric)
        self._save_metrics()
        logger.info(
            f"Recorded metric for session {metric.session_id}: "
            f"{metric.game_result}, {metric.survival_time_seconds:.1f}s survival"
        )

    def get_aggregate_stats(self, last_n: Optional[int] = None) -> Dict[str, Any]:
        """
        Get aggregated statistics.

        Args:
            last_n: Only consider last N sessions (None = all)

        Returns:
            Dictionary of aggregate statistics
        """
        metrics_to_analyze = self.metrics[-last_n:] if last_n else self.metrics

        if not metrics_to_analyze:
            return {
                "total_sessions": 0,
                "win_rate": 0.0,
                "avg_survival_time": 0.0,
                "unique_endings_found": 0,
                "total_wins": 0,
                "total_losses": 0,
            }

        total_sessions = len(metrics_to_analyze)
        wins = sum(1 for m in metrics_to_analyze if m.game_result == "win")
        losses = sum(1 for m in metrics_to_analyze if m.game_result == "loss")
        crashes = sum(1 for m in metrics_to_analyze if m.game_result == "crash")

        avg_survival = (
            sum(m.survival_time_seconds for m in metrics_to_analyze) / total_sessions
        )

        unique_endings = set(
            m.unique_ending_id
            for m in metrics_to_analyze
            if m.unique_ending_id is not None
        )

        total_actions = sum(m.actions_taken for m in metrics_to_analyze)
        total_loops = sum(m.loops_detected for m in metrics_to_analyze)

        return {
            "total_sessions": total_sessions,
            "win_rate": wins / total_sessions if total_sessions > 0 else 0.0,
            "avg_survival_time": avg_survival,
            "unique_endings_found": len(unique_endings),
            "total_wins": wins,
            "total_losses": losses,
            "total_crashes": crashes,
            "total_actions": total_actions,
            "total_loops_detected": total_loops,
            "avg_actions_per_session": (
                total_actions / total_sessions if total_sessions > 0 else 0
            ),
        }

    def get_recent_performance(self, window: int = 10) -> Dict[str, Any]:
        """Get performance over recent sessions."""
        return self.get_aggregate_stats(last_n=window)

    def has_improved(self, window: int = 10, baseline_window: int = 100) -> bool:
        """
        Check if agent has improved over time.

        Args:
            window: Recent sessions to compare
            baseline_window: Baseline sessions for comparison

        Returns:
            True if recent performance exceeds baseline
        """
        if len(self.metrics) < window + baseline_window:
            return False

        baseline_stats = self.get_aggregate_stats(last_n=baseline_window)
        recent_stats = self.get_recent_performance(window=window)

        # Compare win rate and survival time
        improved_win_rate = recent_stats["win_rate"] > baseline_stats["win_rate"]
        improved_survival = (
            recent_stats["avg_survival_time"] > baseline_stats["avg_survival_time"]
        )

        return improved_win_rate or improved_survival

    def clear_metrics(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
        self._save_metrics()
        logger.info("Cleared all metrics")
