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
import json
from typing import Any, List, Dict, Optional
from pathlib import Path
from datetime import datetime

from src.lib.types import GameState, Action, Session
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
        if hasattr(self, "conn") and self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass

    def _initialize_database(self) -> None:
        """
        Initialize database schema if it doesn't exist.

        Creates all necessary tables for comprehensive data storage.
        """
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Access columns by name

            cursor = self.conn.cursor()
            
            # Episodes table - High-level episode metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    total_actions INTEGER DEFAULT 0,
                    duration_seconds REAL,
                    outcome TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_id ON episodes(agent_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_start_time ON episodes(start_time)
            """)
            
            # Game states table - Captured game states
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    episode_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    screenshot_path TEXT,
                    ocr_text TEXT,
                    detected_elements TEXT,
                    window_bounds TEXT,
                    state_hash TEXT,
                    FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_gs_episode_id ON game_states(episode_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_gs_timestamp ON game_states(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_gs_state_hash ON game_states(state_hash)
            """)
            
            # Actions table - Actions taken
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    episode_id INTEGER NOT NULL,
                    state_id INTEGER,
                    action_type TEXT NOT NULL,
                    parameters TEXT,
                    success BOOLEAN DEFAULT 1,
                    timestamp TIMESTAMP NOT NULL,
                    execution_time_ms REAL,
                    FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE,
                    FOREIGN KEY (state_id) REFERENCES game_states(id) ON DELETE SET NULL
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_act_episode_id ON actions(episode_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_act_action_type ON actions(action_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_act_timestamp ON actions(timestamp)
            """)
            
            # Experiences table - State-Action-Reward-State tuples
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    episode_id INTEGER NOT NULL,
                    state_id INTEGER NOT NULL,
                    action_id INTEGER NOT NULL,
                    next_state_id INTEGER,
                    reward REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE,
                    FOREIGN KEY (state_id) REFERENCES game_states(id) ON DELETE CASCADE,
                    FOREIGN KEY (action_id) REFERENCES actions(id) ON DELETE CASCADE,
                    FOREIGN KEY (next_state_id) REFERENCES game_states(id) ON DELETE SET NULL
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_exp_episode_id ON experiences(episode_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_exp_reward ON experiences(reward)
            """)
            
            # Mechanics table - Learned game rules
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanics (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    conditions TEXT,
                    effects TEXT,
                    confidence REAL DEFAULT 0.0,
                    observations INTEGER DEFAULT 1,
                    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Patterns table - Discovered action patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    sequence TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    success_rate REAL DEFAULT 0.0,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pat_pattern_type ON patterns(pattern_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pat_frequency ON patterns(frequency)
            """)
            
            self.conn.commit()
            logger.debug("database_schema_initialized", tables=6)

        except Exception as e:
            logger.error("database_connection_failed", error=str(e))
            raise

    def start_episode(self, agent_id: str) -> int:
        """
        Start a new episode and return its ID.
        
        Args:
            agent_id: Identifier for the agent
            
        Returns:
            Episode ID
        """
        if not self.conn:
            raise RuntimeError("Database connection not initialized")
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO episodes (agent_id, start_time, total_actions)
                VALUES (?, ?, 0)
            """, (agent_id, datetime.now().isoformat()))
            self.conn.commit()
            
            episode_id = cursor.lastrowid
            logger.info("episode_started", episode_id=episode_id, agent_id=agent_id)
            return episode_id
            
        except Exception as e:
            logger.error("failed_to_start_episode", error=str(e))
            raise
    
    def end_episode(self, episode_id: int, outcome: str = "completed") -> None:
        """
        Mark an episode as complete.
        
        Args:
            episode_id: Episode to complete
            outcome: Outcome ('completed', 'victory', 'defeat', 'timeout', 'interrupted')
        """
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # Get start time to calculate duration
            cursor.execute("SELECT start_time FROM episodes WHERE id = ?", (episode_id,))
            row = cursor.fetchone()
            if not row:
                return
            
            start_time = datetime.fromisoformat(row[0])
            duration = (datetime.now() - start_time).total_seconds()
            
            cursor.execute("""
                UPDATE episodes 
                SET end_time = ?, duration_seconds = ?, outcome = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), duration, outcome, episode_id))
            
            self.conn.commit()
            logger.info("episode_ended", episode_id=episode_id, outcome=outcome, duration=duration)
            
        except Exception as e:
            logger.error("failed_to_end_episode", error=str(e), episode_id=episode_id)
    
    def store_game_state(
        self, 
        episode_id: int, 
        state: GameState,
        screenshot_path: Optional[str] = None
    ) -> int:
        """
        Store a game state.
        
        Args:
            episode_id: Episode this state belongs to
            state: Game state object
            screenshot_path: Optional path to saved screenshot
            
        Returns:
            State ID
        """
        if not self.conn:
            raise RuntimeError("Database connection not initialized")
            
        try:
            cursor = self.conn.cursor()
            
            # Create state hash for deduplication
            state_data = {
                'text': getattr(state, 'text_elements', []),
                'bounds': str(getattr(state, 'window_bounds', ''))
            }
            state_hash = str(hash(json.dumps(state_data, sort_keys=True)))
            
            cursor.execute("""
                INSERT INTO game_states (
                    episode_id, timestamp, screenshot_path, 
                    ocr_text, detected_elements, window_bounds, state_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                episode_id,
                datetime.now().isoformat(),
                screenshot_path,
                json.dumps(getattr(state, 'text_elements', [])),
                json.dumps(getattr(state, 'detected_elements', [])),
                json.dumps(str(getattr(state, 'window_bounds', ''))),
                state_hash
            ))
            
            self.conn.commit()
            state_id = cursor.lastrowid
            
            logger.debug("game_state_stored", state_id=state_id, episode_id=episode_id)
            return state_id
            
        except Exception as e:
            logger.error("failed_to_store_game_state", error=str(e))
            raise
    
    def store_action(
        self,
        episode_id: int,
        state_id: Optional[int],
        action: Action,
        success: bool = True,
        execution_time_ms: Optional[float] = None
    ) -> int:
        """
        Store an action.
        
        Args:
            episode_id: Episode this action belongs to
            state_id: State when action was taken (optional)
            action: Action object
            success: Whether action executed successfully
            execution_time_ms: How long action took to execute
            
        Returns:
            Action ID
        """
        if not self.conn:
            raise RuntimeError("Database connection not initialized")
            
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO actions (
                    episode_id, state_id, action_type, parameters,
                    success, timestamp, execution_time_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                episode_id,
                state_id,
                action.action_type.value if hasattr(action, 'action_type') else 'UNKNOWN',
                json.dumps({k: str(v) for k, v in action.parameters.items()} if hasattr(action, 'parameters') else {}),
                success,
                datetime.now().isoformat(),
                execution_time_ms
            ))
            
            # Update episode action count
            cursor.execute("""
                UPDATE episodes 
                SET total_actions = total_actions + 1
                WHERE id = ?
            """, (episode_id,))
            
            self.conn.commit()
            action_id = cursor.lastrowid
            
            logger.debug("action_stored", action_id=action_id, episode_id=episode_id)
            return action_id
            
        except Exception as e:
            logger.error("failed_to_store_action", error=str(e))
            raise

    def store_experience(
        self, 
        episode_id: int,
        state_id: int,
        action_id: int,
        next_state_id: Optional[int],
        reward: float
    ) -> int:
        """
        Store a State-Action-Reward-State experience tuple.

        Args:
            episode_id: Episode this experience belongs to
            state_id: Current state ID
            action_id: Action taken ID
            next_state_id: Resulting state ID (optional)
            reward: Reward received
            
        Returns:
            Experience ID
        """
        if not self.conn:
            raise RuntimeError("Database connection not initialized")
            
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO experiences (
                    episode_id, state_id, action_id, next_state_id, reward
                )
                VALUES (?, ?, ?, ?, ?)
            """, (episode_id, state_id, action_id, next_state_id, reward))
            
            self.conn.commit()
            experience_id = cursor.lastrowid
            
            logger.debug("experience_stored", 
                        experience_id=experience_id,
                        episode_id=episode_id, 
                        reward=reward)
            return experience_id
            
        except Exception as e:
            logger.error("failed_to_store_experience", error=str(e))
            raise

    def store_mechanic(self, mechanic_name: str, data: Dict[str, Any]) -> None:
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
            description = data.get("description", "")
            conditions = data.get("conditions", {})
            effects = data.get("effects", {})

            # Store everything as JSON in conditions field for flexibility
            full_data = {
                "description": description,
                "conditions": conditions,
                "effects": effects,
                **{
                    k: v
                    for k, v in data.items()
                    if k not in ["description", "conditions", "effects"]
                },
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
                    json.dumps(full_data),  # Store full data in effects field
                ),
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
            cursor.execute("SELECT * FROM mechanics WHERE name = ?", (mechanic_name,))
            row = cursor.fetchone()

            if row:
                # Parse the full data from effects field
                full_data = json.loads(row["effects"])
                result = {
                    "mechanic_id": row["name"],  # Use name as mechanic_id
                    "name": row["name"],
                    **full_data,  # Include all stored fields
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
                    "conditions": json.loads(row["conditions"]) if row["conditions"] else {},
                    "effects": json.loads(row["effects"]) if row["effects"] else {},
                    "learned_at": row["learned_at"],
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Failed to list mechanics: {e}")
            return []
    
    def get_episode_stats(self, episode_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for an episode."""
        if not self.conn:
            return None
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    e.*,
                    COUNT(DISTINCT s.id) as state_count,
                    COUNT(DISTINCT a.id) as action_count,
                    COUNT(DISTINCT ex.id) as experience_count,
                    AVG(ex.reward) as avg_reward
                FROM episodes e
                LEFT JOIN game_states s ON s.episode_id = e.id
                LEFT JOIN actions a ON a.episode_id = e.id
                LEFT JOIN experiences ex ON ex.episode_id = e.id
                WHERE e.id = ?
                GROUP BY e.id
            """, (episode_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return dict(row)
            
        except Exception as e:
            logger.error("failed_to_get_episode_stats", error=str(e))
            return None
    
    def get_recent_episodes(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent episodes for an agent."""
        if not self.conn:
            return []
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM episodes 
                WHERE agent_id = ?
                ORDER BY start_time DESC
                LIMIT ?
            """, (agent_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error("failed_to_get_recent_episodes", error=str(e))
            return []
    
    def get_total_experiences(self) -> int:
        """Get total number of stored experiences."""
        if not self.conn:
            return 0
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM experiences")
            row = cursor.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0
    
    def vacuum(self) -> None:
        """Compact the database to reclaim space."""
        if not self.conn:
            return
            
        try:
            logger.info("vacuuming_database")
            self.conn.execute("VACUUM")
            logger.info("database_vacuumed")
        except Exception as e:
            logger.error("vacuum_failed", error=str(e))

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("database_connection_closed")
