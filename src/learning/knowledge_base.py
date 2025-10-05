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
        
        Creates the mechanics table for storing learned game rules.
        """
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            
            # Create mechanics table if it doesn't exist
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanics (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    conditions TEXT,
                    effects TEXT,
                    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
            
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
    
    def store_mechanic(
        self,
        mechanic_name: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Store a learned game mechanic.
        T098: Implement store_mechanic() for game rules.
        
        Args:
            mechanic_name: Name/identifier for the mechanic
            data: Dictionary containing mechanic data (description, conditions, effects, etc.)
        """
        try:
            import json
            cursor = self.conn.cursor()
            
            # Extract standard fields
            description = data.get('description', '')
            conditions = data.get('conditions', {})
            effects = data.get('effects', {})
            
            # Store everything as JSON in conditions field for flexibility
            full_data = {
                'description': description,
                'conditions': conditions,
                'effects': effects,
                **{k: v for k, v in data.items() if k not in ['description', 'conditions', 'effects']}
            }
            
            cursor.execute(
                """
                INSERT OR REPLACE INTO mechanics (name, description, conditions, effects, learned_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                """,
                (
                    mechanic_name,
                    description,
                    json.dumps(conditions),
                    json.dumps(full_data)  # Store full data in effects field
                )
            )
            
            self.conn.commit()
            logger.info(f"Stored mechanic: {mechanic_name}")
            
        except Exception as e:
            logger.error(f"Failed to store mechanic: {e}")
    
    def get_mechanic(self, mechanic_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a learned mechanic by name."""
        try:
            import json
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM mechanics WHERE name = ?",
                (mechanic_name,)
            )
            row = cursor.fetchone()
            
            if row:
                # Parse the full data from effects field
                full_data = json.loads(row["effects"])
                result = {
                    "mechanic_id": row["name"],  # Use name as mechanic_id
                    "name": row["name"],
                    **full_data  # Include all stored fields
                }
                return result
            return None
            
        except Exception as e:
            logger.error(f"Failed to get mechanic: {e}")
            return None
    
    def list_mechanics(self) -> List[Dict[str, Any]]:
        """List all learned mechanics."""
        try:
            import json
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM mechanics ORDER BY learned_at DESC")
            rows = cursor.fetchall()
            
            return [
                {
                    "mechanic_id": row["name"],  # Use name as mechanic_id
                    "name": row["name"],
                    "description": row["description"],
                    "conditions": json.loads(row["conditions"]),
                    "effects": json.loads(row["effects"]),
                    "learned_at": row["learned_at"]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to list mechanics: {e}")
            return []
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("database_connection_closed")
