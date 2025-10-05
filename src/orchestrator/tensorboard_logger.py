"""
TensorBoard Logging for Training Metrics

T119: Real-time training metrics visualization with TensorBoard.

Logs:
- Episode rewards
- Episode lengths
- Win/loss rates
- Average survival time
- Loop detection events
- Action success rates
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json

try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False
    SummaryWriter = None

from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class TensorBoardLogger:
    """
    TensorBoard metrics logger for training visualization.
    
    Writes metrics to TensorBoard log directory for real-time monitoring.
    Falls back to JSON logging if TensorBoard is not available.
    """
    
    def __init__(
        self,
        log_dir: Optional[Path] = None,
        agent_id: str = "agent"
    ):
        """
        Initialize TensorBoard logger.
        
        Args:
            log_dir: Directory for TensorBoard logs (default: data/logs/tensorboard)
            agent_id: Agent identifier for namespacing metrics
        """
        self.agent_id = agent_id
        
        if log_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_dir = Path(f"data/logs/tensorboard/{agent_id}_{timestamp}")
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize TensorBoard writer if available
        self.writer: Optional[SummaryWriter] = None
        if TENSORBOARD_AVAILABLE:
            self.writer = SummaryWriter(str(self.log_dir))
            logger.info(
                "tensorboard_initialized",
                log_dir=str(self.log_dir),
                agent_id=agent_id
            )
        else:
            logger.warning(
                "tensorboard_unavailable",
                fallback="json_logging",
                message="Install tensorboard: pip install tensorboard"
            )
            # Create JSON log file as fallback
            self.json_log_path = self.log_dir / "metrics.jsonl"
    
    def log_episode(
        self,
        episode_num: int,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Log metrics for a completed episode.
        
        Args:
            episode_num: Episode number (used as step in TensorBoard)
            metrics: Dictionary of metrics to log
        """
        if self.writer:
            # Log to TensorBoard
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    self.writer.add_scalar(f"episode/{key}", value, episode_num)
        else:
            # Fallback to JSON logging
            log_entry = {
                "episode": episode_num,
                "timestamp": datetime.now().isoformat(),
                **metrics
            }
            with open(self.json_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        logger.debug(
            "episode_metrics_logged",
            episode=episode_num,
            metrics=metrics
        )
    
    def log_scalar(
        self,
        tag: str,
        value: float,
        step: int
    ) -> None:
        """
        Log a scalar metric.
        
        Args:
            tag: Metric name
            value: Metric value
            step: Training step
        """
        if self.writer:
            self.writer.add_scalar(tag, value, step)
        else:
            log_entry = {
                "tag": tag,
                "value": value,
                "step": step,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.json_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
    
    def log_histogram(
        self,
        tag: str,
        values: list,
        step: int
    ) -> None:
        """
        Log a histogram of values.
        
        Args:
            tag: Histogram name
            values: List of values
            step: Training step
        """
        if self.writer:
            import torch
            self.writer.add_histogram(tag, torch.tensor(values), step)
    
    def log_text(
        self,
        tag: str,
        text: str,
        step: int
    ) -> None:
        """
        Log text (e.g., strategy articulation).
        
        Args:
            tag: Text identifier
            text: Text content
            step: Training step
        """
        if self.writer:
            self.writer.add_text(tag, text, step)
        else:
            log_entry = {
                "tag": tag,
                "text": text,
                "step": step,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.json_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
    
    def close(self) -> None:
        """Close the TensorBoard writer."""
        if self.writer:
            self.writer.close()
            logger.info("tensorboard_closed", log_dir=str(self.log_dir))


def create_logger(
    agent_id: str,
    log_dir: Optional[Path] = None
) -> TensorBoardLogger:
    """
    Create a TensorBoard logger instance.
    
    Args:
        agent_id: Agent identifier
        log_dir: Optional custom log directory
        
    Returns:
        TensorBoardLogger instance
    """
    return TensorBoardLogger(log_dir=log_dir, agent_id=agent_id)
