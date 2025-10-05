"""
Knowledge Base - SQLite-based Experience Storage

This module provides persistent storage for:
- Game sessions and episodes
- State-action-reward experiences
- Learned mechanics and patterns
- Performance metrics

Uses SQLite for local storage with efficient querying.
"""

import sqlite3
from typing import Any, List, Dict, Optional
from pathlib import Path

from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class KnowledgeBase:
    """
    SQLite-based knowledge base for agent learning.
    
    Stores:
    - Sessions: Complete gameplay episodes
    - Experiences: SARS tuples for training
    - Mechanics: Learned game rules
    - Strategies: Successful action sequences
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize knowledge base connection.
        
        Args:
            db_path: Path to SQLite database (default: data/knowledge_base.db)
        """
        if db_path is None:
            db_path = "data/knowledge_base.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = None
        self._initialize_database()
        
        logger.info("knowledge_base_initialized", db_path=str(self.db_path))
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed."""
        self.close()
        return False
    
    def __del__(self):
        """Cleanup - ensure connection is closed."""
        if hasattr(self, 'conn') and self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
    
    def _initialize_database(self) -> None:
        """
        Initialize database schema if it doesn't exist.
        
        Note: Schema was created by T007 during setup.
        This just ensures connection is established.
        """
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            
            logger.debug("database_connection_established")
            
        except Exception as e:
            logger.error("database_connection_failed", error=str(e))
            raise
    
    def store_experience(
        self,
        state: Any,
        action: Any,
        next_state: Any,
        reward: float
    ) -> None:
        """
        Store a single experience tuple (SARS).
        
        Args:
            state: Current game state
            action: Action taken
            next_state: Resulting game state
            reward: Reward received
        """
        # Placeholder implementation
        # TODO T096: Implement actual storage
        logger.debug(
            "experience_stored",
            reward=reward
        )
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("database_connection_closed")
