"""
Storage Manager - Automated Data Storage and Cleanup

Handles:
- Screenshot persistence
- Log rotation and archival
- Database storage coordination
- Automatic cleanup
- Storage monitoring
"""

import gzip
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from PIL import Image
import numpy as np

from src.lib.types import GameState, Action
from src.lib.logging_config import get_logger
from src.learning.knowledge_base import KnowledgeBase

logger = get_logger(__name__)


class StorageManager:
    """
    Manages all data storage operations with automatic cleanup and rotation.
    """
    
    def __init__(self, config_path: str = "config/storage.yaml"):
        """
        Initialize storage manager.
        
        Args:
            config_path: Path to storage configuration file
        """
        self.config = self._load_config(config_path)
        self.base_dir = Path("data")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Track current episode for storage
        self.current_episode_id: Optional[int] = None
        self.current_episode_dir: Optional[Path] = None
        self.action_count = 0
        
        # Initialize knowledge base if enabled
        self.kb: Optional[KnowledgeBase] = None
        if self.config['storage']['enable_database_storage']:
            db_path = self.config['storage']['db_path']
            self.kb = KnowledgeBase(db_path)
            logger.info("knowledge_base_enabled", db_path=db_path)
        
        logger.info("storage_manager_initialized", config=self.config)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load storage configuration."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load storage config: {e}, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default storage configuration."""
        return {
            'storage': {
                'enable_database_storage': True,
                'db_path': 'data/knowledge_base.db',
                'save_screenshots': False,
                'screenshot_interval': 5,
                'screenshot_format': 'png',
                'screenshot_quality': 85,
                'log_retention_days': 30,
                'compress_archived_logs': True,
                'tensorboard_keep_runs': 10,
                'checkpoint_retention': 50,
                'auto_cleanup_enabled': False,
                'max_total_storage_gb': 10,
                'warn_storage_gb': 5,
            },
            'performance': {
                'batch_insert_size': 100,
                'commit_interval_seconds': 5,
                'enable_write_ahead_log': True,
            }
        }
    
    def start_episode(self, agent_id: str) -> Optional[int]:
        """
        Start a new episode and prepare storage.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Episode ID if database storage enabled, None otherwise
        """
        self.action_count = 0
        
        # Create episode in database
        if self.kb:
            try:
                self.current_episode_id = self.kb.start_episode(agent_id)
                logger.info("episode_storage_started", episode_id=self.current_episode_id)
            except Exception as e:
                logger.error("failed_to_start_episode_storage", error=str(e))
                self.current_episode_id = None
        
        # Create episode directory for screenshots if enabled
        if self.config['storage']['save_screenshots']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_episode_dir = self.base_dir / "sessions" / "screenshots" / f"episode_{timestamp}"
            self.current_episode_dir.mkdir(parents=True, exist_ok=True)
            logger.info("screenshot_storage_enabled", directory=str(self.current_episode_dir))
        
        return self.current_episode_id
    
    def end_episode(self, outcome: str = "completed") -> None:
        """
        End current episode.
        
        Args:
            outcome: Episode outcome ('completed', 'victory', 'defeat', 'timeout', 'interrupted')
        """
        if self.kb and self.current_episode_id:
            try:
                self.kb.end_episode(self.current_episode_id, outcome)
                logger.info("episode_storage_ended", 
                           episode_id=self.current_episode_id, 
                           outcome=outcome,
                           total_actions=self.action_count)
            except Exception as e:
                logger.error("failed_to_end_episode_storage", error=str(e))
        
        self.current_episode_id = None
        self.current_episode_dir = None
        self.action_count = 0
    
    def store_state_action(
        self,
        state: GameState,
        action: Action,
        screenshot: Optional[np.ndarray] = None,
        success: bool = True,
        execution_time_ms: Optional[float] = None
    ) -> tuple[Optional[int], Optional[int]]:
        """
        Store a state and action.
        
        Args:
            state: Game state
            action: Action taken
            screenshot: Optional screenshot array
            success: Whether action succeeded
            execution_time_ms: Execution time in milliseconds
            
        Returns:
            Tuple of (state_id, action_id) if database enabled, (None, None) otherwise
        """
        if not self.kb or not self.current_episode_id:
            return (None, None)
        
        state_id = None
        action_id = None
        screenshot_path = None
        
        try:
            # Save screenshot if enabled
            if screenshot is not None and self.should_save_screenshot():
                screenshot_path = self._save_screenshot(screenshot)
            
            # Store state
            state_id = self.kb.store_game_state(
                self.current_episode_id,
                state,
                screenshot_path
            )
            
            # Store action
            action_id = self.kb.store_action(
                self.current_episode_id,
                state_id,
                action,
                success,
                execution_time_ms
            )
            
            self.action_count += 1
            
        except Exception as e:
            logger.error("failed_to_store_state_action", error=str(e))
        
        return (state_id, action_id)
    
    def store_experience(
        self,
        state_id: int,
        action_id: int,
        next_state_id: Optional[int],
        reward: float
    ) -> Optional[int]:
        """
        Store an experience (SARS tuple).
        
        Args:
            state_id: Current state ID
            action_id: Action taken ID
            next_state_id: Next state ID (optional)
            reward: Reward received
            
        Returns:
            Experience ID if successful, None otherwise
        """
        if not self.kb or not self.current_episode_id:
            return None
        
        try:
            return self.kb.store_experience(
                self.current_episode_id,
                state_id,
                action_id,
                next_state_id,
                reward
            )
        except Exception as e:
            logger.error("failed_to_store_experience", error=str(e))
            return None
    
    def should_save_screenshot(self) -> bool:
        """Check if we should save a screenshot based on configuration."""
        if not self.config['storage']['save_screenshots']:
            return False
        
        interval = self.config['storage']['screenshot_interval']
        return self.action_count % interval == 0
    
    def _save_screenshot(self, screenshot: np.ndarray) -> str:
        """
        Save a screenshot to disk.
        
        Args:
            screenshot: Screenshot as numpy array
            
        Returns:
            Path to saved screenshot
        """
        if not self.current_episode_dir:
            raise RuntimeError("No current episode directory")
        
        filename = f"action_{self.action_count:04d}.{self.config['storage']['screenshot_format']}"
        filepath = self.current_episode_dir / filename
        
        try:
            # Convert numpy array to PIL Image
            if screenshot.dtype != np.uint8:
                screenshot = (screenshot * 255).astype(np.uint8)
            
            img = Image.fromarray(screenshot)
            
            # Save with appropriate format and quality
            if self.config['storage']['screenshot_format'] == 'jpg':
                img.save(filepath, 'JPEG', quality=self.config['storage']['screenshot_quality'])
            else:
                img.save(filepath, 'PNG')
            
            logger.debug("screenshot_saved", path=str(filepath))
            return str(filepath)
            
        except Exception as e:
            logger.error("failed_to_save_screenshot", error=str(e))
            raise
    
    def cleanup_old_data(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Clean up old data based on retention policies.
        
        Args:
            dry_run: If True, only report what would be cleaned
            
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            'logs_archived': 0,
            'logs_deleted': 0,
            'tensorboard_runs_deleted': 0,
            'checkpoints_deleted': 0,
            'bytes_freed': 0
        }
        
        if not self.config['storage']['auto_cleanup_enabled'] and not dry_run:
            logger.info("auto_cleanup_disabled")
            return stats
        
        logger.info(f"cleanup_started{'_dry_run' if dry_run else ''}")
        
        # Clean old logs
        stats.update(self._cleanup_logs(dry_run))
        
        # Clean old TensorBoard runs
        stats.update(self._cleanup_tensorboard(dry_run))
        
        # Clean old checkpoints
        stats.update(self._cleanup_checkpoints(dry_run))
        
        # Vacuum database
        if not dry_run and self.kb:
            self.kb.vacuum()
        
        logger.info("cleanup_completed", stats=stats)
        return stats
    
    def _cleanup_logs(self, dry_run: bool) -> Dict[str, int]:
        """Clean up old log files."""
        stats = {'logs_archived': 0, 'logs_deleted': 0}
        
        logs_dir = self.base_dir / "logs"
        if not logs_dir.exists():
            return stats
        
        archive_dir = logs_dir / "archive"
        cutoff_date = datetime.now() - timedelta(days=self.config['storage']['log_retention_days'])
        
        for log_file in logs_dir.glob("agent_*.jsonl"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                if not dry_run:
                    archive_dir.mkdir(exist_ok=True)
                    archive_path = archive_dir / log_file.name
                    shutil.move(str(log_file), str(archive_path))
                    
                    if self.config['storage']['compress_archived_logs']:
                        with open(archive_path, 'rb') as f_in:
                            with gzip.open(f"{archive_path}.gz", 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        archive_path.unlink()
                    
                stats['logs_archived'] += 1
        
        return stats
    
    def _cleanup_tensorboard(self, dry_run: bool) -> Dict[str, int]:
        """Clean up old TensorBoard runs."""
        stats = {'tensorboard_runs_deleted': 0}
        
        tb_dir = self.base_dir / "tensorboard"
        if not tb_dir.exists():
            return stats
        
        runs = sorted(tb_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        keep = self.config['storage']['tensorboard_keep_runs']
        
        for old_run in runs[keep:]:
            if not dry_run:
                shutil.rmtree(old_run)
            stats['tensorboard_runs_deleted'] += 1
        
        return stats
    
    def _cleanup_checkpoints(self, dry_run: bool) -> Dict[str, int]:
        """Clean up old checkpoints."""
        stats = {'checkpoints_deleted': 0}
        
        checkpoint_dir = self.base_dir / "checkpoints"
        if not checkpoint_dir.exists():
            return stats
        
        checkpoints = sorted(checkpoint_dir.glob("checkpoint_*.txt"), 
                           key=lambda p: p.stat().st_mtime, 
                           reverse=True)
        keep = self.config['storage']['checkpoint_retention']
        
        for old_checkpoint in checkpoints[keep:]:
            if not dry_run:
                old_checkpoint.unlink()
            stats['checkpoints_deleted'] += 1
        
        return stats
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get current storage usage information."""
        def get_size(path: Path) -> int:
            if path.is_file():
                return path.stat().st_size
            total = 0
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
            return total
        
        info = {
            'total_bytes': 0,
            'logs_bytes': 0,
            'tensorboard_bytes': 0,
            'checkpoints_bytes': 0,
            'database_bytes': 0,
            'screenshots_bytes': 0,
            'total_gb': 0.0
        }
        
        if (self.base_dir / "logs").exists():
            info['logs_bytes'] = get_size(self.base_dir / "logs")
        
        if (self.base_dir / "tensorboard").exists():
            info['tensorboard_bytes'] = get_size(self.base_dir / "tensorboard")
        
        if (self.base_dir / "checkpoints").exists():
            info['checkpoints_bytes'] = get_size(self.base_dir / "checkpoints")
        
        db_path = Path(self.config['storage']['db_path'])
        if db_path.exists():
            info['database_bytes'] = db_path.stat().st_size
        
        if (self.base_dir / "sessions").exists():
            info['screenshots_bytes'] = get_size(self.base_dir / "sessions")
        
        info['total_bytes'] = sum([
            info['logs_bytes'],
            info['tensorboard_bytes'],
            info['checkpoints_bytes'],
            info['database_bytes'],
            info['screenshots_bytes']
        ])
        
        info['total_gb'] = info['total_bytes'] / (1024 ** 3)
        
        # Check against limits
        warn_threshold = self.config['storage']['warn_storage_gb']
        max_threshold = self.config['storage']['max_total_storage_gb']
        
        if info['total_gb'] >= max_threshold:
            logger.warning("storage_limit_exceeded", total_gb=info['total_gb'], limit=max_threshold)
        elif info['total_gb'] >= warn_threshold:
            logger.warning("storage_warning", total_gb=info['total_gb'], threshold=warn_threshold)
        
        return info
    
    def close(self) -> None:
        """Close storage manager and cleanup resources."""
        if self.kb:
            self.kb.close()
        logger.info("storage_manager_closed")
