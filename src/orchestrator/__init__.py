"""
Orchestrator - Autonomous AI Agent Coordination

This module coordinates all agent libraries into a cohesive autonomous system:
- Vision: Captures game state
- NLP: Understands narrative text
- Learning: Selects actions and learns from experience
- Safety: Validates all actions (100% reliability)
- Automation: Executes safe actions

Public API:
- run_episode(agent_id, window_name, max_actions) -> Session
- train_agent(agent_id, num_episodes, window_name) -> List[Session]
- get_agent_metrics(agent_id) -> Dict
- articulate_strategy(agent_id) -> str

The orchestrator implements the perception-decision-action loop and manages
the agent's learning process across multiple episodes.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path

from .agent_runner import AgentRunner, TrainingRunner
from src.lib.types import Session
from src.lib.logging_config import get_logger

logger = get_logger(__name__)

__all__ = [
    'run_episode',
    'train_agent',
    'get_agent_metrics',
    'articulate_strategy',
    'AgentRunner',
    'TrainingRunner',
]

# Global registry of agent runners
_agent_runners: Dict[str, AgentRunner] = {}


def _get_or_create_runner(
    agent_id: str,
    window_name: str = "Cultist Simulator",
    max_actions_per_episode: int = 1000
) -> AgentRunner:
    """
    Get existing agent runner or create new one.
    
    Args:
        agent_id: Unique agent identifier
        window_name: Game window name
        max_actions_per_episode: Maximum actions per episode
        
    Returns:
        AgentRunner instance
    """
    if agent_id not in _agent_runners:
        _agent_runners[agent_id] = AgentRunner(
            agent_id=agent_id,
            window_name=window_name,
            max_actions_per_episode=max_actions_per_episode
        )
        logger.info("agent_runner_created", agent_id=agent_id)
    
    return _agent_runners[agent_id]


def run_episode(
    agent_id: str = "agent_001",
    window_name: str = "Cultist Simulator",
    max_actions: int = 1000,
    max_duration_seconds: Optional[float] = None
) -> Session:
    """
    Run a single autonomous episode.
    
    T106-T108: Episode execution with integrated pipeline.
    
    The agent will:
    1. Capture game state (vision)
    2. Understand narrative (NLP)
    3. Select actions (learning)
    4. Validate actions (safety)
    5. Execute actions (automation)
    6. Record experiences
    7. Detect and avoid loops
    
    Args:
        agent_id: Unique agent identifier
        window_name: Name of game window to control
        max_actions: Maximum actions before ending episode
        max_duration_seconds: Maximum episode duration
        
    Returns:
        Completed Session object
        
    Example:
        >>> session = run_episode(
        ...     agent_id="test_agent",
        ...     window_name="Cultist Simulator",
        ...     max_actions=100
        ... )
        >>> print(f"Episode completed: {session.total_actions} actions")
    """
    runner = _get_or_create_runner(
        agent_id=agent_id,
        window_name=window_name,
        max_actions_per_episode=max_actions
    )
    
    logger.info(
        "run_episode_start",
        agent_id=agent_id,
        window_name=window_name,
        max_actions=max_actions
    )
    
    session = runner.run_episode(max_duration_seconds=max_duration_seconds)
    
    logger.info(
        "run_episode_complete",
        agent_id=agent_id,
        session_id=session.session_id,
        actions=session.total_actions
    )
    
    return session


def train_agent(
    agent_id: str = "agent_001",
    num_episodes: int = 100,
    window_name: str = "Cultist Simulator",
    max_actions_per_episode: int = 1000,
    max_episode_duration: Optional[float] = 300.0,
    checkpoint_interval: int = 10
) -> List[Session]:
    """
    Train agent across multiple episodes.
    
    T109: Training loop (100-500 episodes).
    T110: Real-time metrics tracking.
    
    The training loop will:
    - Run multiple episodes
    - Track performance metrics
    - Save checkpoints
    - Learn from experience
    
    Args:
        agent_id: Unique agent identifier
        num_episodes: Number of training episodes
        window_name: Name of game window
        max_actions_per_episode: Maximum actions per episode
        max_episode_duration: Maximum seconds per episode
        checkpoint_interval: Save checkpoint every N episodes
        
    Returns:
        List of completed sessions
        
    Example:
        >>> sessions = train_agent(
        ...     agent_id="learner_001",
        ...     num_episodes=50,
        ...     max_actions_per_episode=500
        ... )
        >>> print(f"Training complete: {len(sessions)} episodes")
    """
    runner = _get_or_create_runner(
        agent_id=agent_id,
        window_name=window_name,
        max_actions_per_episode=max_actions_per_episode
    )
    
    trainer = TrainingRunner(runner)
    
    logger.info(
        "train_agent_start",
        agent_id=agent_id,
        num_episodes=num_episodes
    )
    
    sessions = trainer.train(
        num_episodes=num_episodes,
        max_episode_duration=max_episode_duration,
        checkpoint_interval=checkpoint_interval
    )
    
    logger.info(
        "train_agent_complete",
        agent_id=agent_id,
        episodes=len(sessions)
    )
    
    return sessions


def get_agent_metrics(agent_id: str = "agent_001") -> Dict[str, Any]:
    """
    Get performance metrics for an agent.
    
    T110: Real-time metrics tracking.
    
    Args:
        agent_id: Agent identifier
        
    Returns:
        Dictionary of metrics including:
        - episodes_completed
        - total_actions
        - successful_actions
        - failed_actions
        - success_rate
        - loops_detected
        - average_episode_length
        
    Example:
        >>> metrics = get_agent_metrics("agent_001")
        >>> print(f"Success rate: {metrics['success_rate']:.1%}")
    """
    if agent_id not in _agent_runners:
        logger.warning("agent_not_found", agent_id=agent_id)
        return {
            'error': 'Agent not found',
            'agent_id': agent_id
        }
    
    runner = _agent_runners[agent_id]
    return runner.get_metrics()


def articulate_strategy(agent_id: str = "agent_001") -> str:
    """
    Get human-readable description of agent's current strategy.
    
    T111: Articulate strategy for human understanding.
    
    Args:
        agent_id: Agent identifier
        
    Returns:
        Natural language strategy description
        
    Example:
        >>> strategy = articulate_strategy("agent_001")
        >>> print(strategy)
        Agent Strategy Summary (ID: agent_001)
        ===========================================
        ...
    """
    if agent_id not in _agent_runners:
        return f"Agent '{agent_id}' not found. No strategy available."
    
    runner = _agent_runners[agent_id]
    return runner.articulate_strategy()
