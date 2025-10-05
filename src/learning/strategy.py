"""
Strategy Module

Handles strategy evolution and management for the RL agent.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import json

from src.lib.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Strategy:
    """
    Represents a high-level gameplay strategy.
    """
    # Make all fields optional with defaults for flexibility
    strategy_id: str = ""
    name: str = ""
    description: str = ""
    goal_priorities: List[str] = field(default_factory=list)
    exploration_rate: float = 0.3
    risk_tolerance: float = 0.5
    
    # Performance tracking
    episodes_played: int = 0  # For test compatibility
    sessions_played: int = 0
    win_rate: float = 0.0
    wins: int = 0
    games_played: int = 0
    avg_survival_time: float = 0.0
    
    # Legacy/optional fields
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    parameters: Dict[str, Any] = field(default_factory=dict)
    performance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set strategy_id from name if not provided."""
        if not self.strategy_id and self.name:
            self.strategy_id = self.name.lower().replace(" ", "_")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "description": self.description,
            "goal_priorities": self.goal_priorities,
            "exploration_rate": self.exploration_rate,
            "risk_tolerance": self.risk_tolerance,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "parameters": self.parameters,
            "performance_score": self.performance_score,
            "games_played": self.games_played,
            "wins": self.wins,
            "sessions_played": self.sessions_played,
            "win_rate": self.win_rate,
            "avg_survival_time": self.avg_survival_time,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Strategy':
        """Deserialize from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
            
        return cls(
            strategy_id=data.get("strategy_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            goal_priorities=data.get("goal_priorities", []),
            exploration_rate=data.get("exploration_rate", 0.3),
            risk_tolerance=data.get("risk_tolerance", 0.5),
            version=data.get("version", 1),
            created_at=created_at,
            parameters=data.get("parameters", {}),
            performance_score=data.get("performance_score", 0.0),
            games_played=data.get("games_played", 0),
            wins=data.get("wins", 0),
            sessions_played=data.get("sessions_played", 0),
            win_rate=data.get("win_rate", 0.0),
            avg_survival_time=data.get("avg_survival_time", 0.0),
            metadata=data.get("metadata", {})
        )


class StrategyManager:
    """
    Manages strategy CRUD operations and evolution.
    T100, T101: Strategy entity operations and evolution.
    """
    
    def __init__(self, storage_path: str = "data/strategies.json"):
        """Initialize strategy manager."""
        self.storage_path = storage_path
        self.strategies: Dict[str, Strategy] = {}
        self._load_strategies()
    
    def _load_strategies(self) -> None:
        """Load strategies from disk."""
        import os
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for strategy_data in data.get("strategies", []):
                        strategy = Strategy.from_dict(strategy_data)
                        self.strategies[strategy.strategy_id] = strategy
                logger.info(f"Loaded {len(self.strategies)} strategies")
            except Exception as e:
                logger.error(f"Failed to load strategies: {e}")
    
    def _save_strategies(self) -> None:
        """Save strategies to disk."""
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            data = {
                "strategies": [s.to_dict() for s in self.strategies.values()]
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.strategies)} strategies")
        except Exception as e:
            logger.error(f"Failed to save strategies: {e}")
    
    def create_strategy(self, strategy_id: str, parameters: Dict[str, Any]) -> Strategy:
        """Create a new strategy."""
        strategy = Strategy(
            strategy_id=strategy_id,
            version=1,
            created_at=datetime.now(),
            parameters=parameters
        )
        self.strategies[strategy_id] = strategy
        self._save_strategies()
        logger.info(f"Created strategy {strategy_id}")
        return strategy
    
    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Get a strategy by ID."""
        return self.strategies.get(strategy_id)
    
    def update_strategy(self, strategy_id: str, **kwargs) -> Optional[Strategy]:
        """Update strategy attributes."""
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            return None
        
        for key, value in kwargs.items():
            if hasattr(strategy, key):
                setattr(strategy, key, value)
        
        self._save_strategies()
        logger.debug(f"Updated strategy {strategy_id}")
        return strategy
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a strategy."""
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            self._save_strategies()
            logger.info(f"Deleted strategy {strategy_id}")
            return True
        return False
    
    def list_strategies(self) -> List[Strategy]:
        """List all strategies."""
        return list(self.strategies.values())
    
    def evolve_strategy(
        self,
        base_strategy_id: str,
        mutation_rate: float = 0.1
    ) -> Optional[Strategy]:
        """
        Create a mutated version of a strategy.
        T101: Strategy evolution through mutation.
        """
        base = self.strategies.get(base_strategy_id)
        if not base:
            return None
        
        import random
        import uuid
        
        # Create mutated parameters
        new_params = base.parameters.copy()
        for key, value in new_params.items():
            if isinstance(value, (int, float)) and random.random() < mutation_rate:
                # Mutate numerical parameters
                mutation = random.gauss(0, 0.1)
                new_params[key] = value * (1 + mutation)
        
        # Create new strategy
        new_strategy = Strategy(
            strategy_id=str(uuid.uuid4()),
            version=base.version + 1,
            created_at=datetime.now(),
            parameters=new_params,
            metadata={"parent_id": base_strategy_id}
        )
        
        self.strategies[new_strategy.strategy_id] = new_strategy
        self._save_strategies()
        
        logger.info(f"Evolved strategy {base_strategy_id} -> {new_strategy.strategy_id}")
        return new_strategy
    
    def merge_strategies(
        self,
        strategy_id_1: str,
        strategy_id_2: str,
        weight: float = 0.5
    ) -> Optional[Strategy]:
        """
        Merge two strategies with weighted averaging.
        T101: Strategy evolution through merging.
        """
        s1 = self.strategies.get(strategy_id_1)
        s2 = self.strategies.get(strategy_id_2)
        
        if not s1 or not s2:
            return None
        
        import uuid
        
        # Merge parameters
        merged_params = {}
        all_keys = set(s1.parameters.keys()) | set(s2.parameters.keys())
        
        for key in all_keys:
            v1 = s1.parameters.get(key, 0)
            v2 = s2.parameters.get(key, 0)
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                merged_params[key] = v1 * weight + v2 * (1 - weight)
            else:
                merged_params[key] = v1 if weight > 0.5 else v2
        
        # Create merged strategy
        merged = Strategy(
            strategy_id=str(uuid.uuid4()),
            version=max(s1.version, s2.version) + 1,
            created_at=datetime.now(),
            parameters=merged_params,
            metadata={
                "parent_1": strategy_id_1,
                "parent_2": strategy_id_2,
                "merge_weight": weight
            }
        )
        
        self.strategies[merged.strategy_id] = merged
        self._save_strategies()
        
        logger.info(f"Merged strategies {strategy_id_1} + {strategy_id_2} -> {merged.strategy_id}")
        return merged
