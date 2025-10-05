"""
Agent Runner - Autonomous Episode Execution

This module orchestrates the autonomous AI agent's gameplay loop:
- Vision: Capture game state
- NLP: Understand narrative text
- Learning: Select optimal actions
- Safety: Validate actions
- Automation: Execute safe actions
- Knowledge: Record experiences

The agent runs episodes, learns from experience, and improves over time.
"""

import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import hashlib

from src.lib.types import (
    GameState, Action, Session, EndCondition, 
    ActionType, Point, Rect
)
from src.lib.logging_config import get_logger
from src.vision import capture_game_state
from src.nlp import analyze_text, extract_goals
from src.learning import (
    select_action, update_knowledge, detect_loop,
    store_session, ModelNotLoadedError
)
from src.safety import validate_action
from src.automation import (
    simulate_click, simulate_key_press, wait,
    OutOfBoundsError, BlacklistedKeyError, WindowNotFocusedError
)

logger = get_logger(__name__)


class AgentRunner:
    """
    Orchestrates autonomous agent gameplay episodes.
    
    Implements the perception-decision-action loop:
    1. Capture game state (vision)
    2. Understand narrative (NLP)
    3. Select action (learning)
    4. Validate action (safety)
    5. Execute action (automation)
    6. Record experience (learning)
    7. Detect loops and adapt
    """
    
    def __init__(
        self,
        agent_id: str,
        window_name: str = "Cultist Simulator",
        max_actions_per_episode: int = 1000,
        loop_detection_window: int = 30
    ):
        """
        Initialize agent runner.
        
        Args:
            agent_id: Unique agent identifier
            window_name: Game window name
            max_actions_per_episode: Maximum actions before ending episode
            loop_detection_window: History size for loop detection
        """
        self.agent_id = agent_id
        self.window_name = window_name
        self.max_actions_per_episode = max_actions_per_episode
        self.loop_detection_window = loop_detection_window
        
        # Current episode state
        self.current_session: Optional[Session] = None
        self.action_history: List[Action] = []
        self.episode_count = 0
        self.total_actions = 0
        
        # Metrics
        self.metrics = {
            'episodes_completed': 0,
            'total_actions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'loops_detected': 0,
            'average_episode_length': 0.0,
        }
        
        logger.info(
            "agent_runner_initialized",
            agent_id=agent_id,
            window_name=window_name,
            max_actions=max_actions_per_episode
        )
    
    def run_episode(self, max_duration_seconds: Optional[float] = None) -> Session:
        """
        Run a single episode until termination.
        
        T106: Episode execution loop.
        T107: Vision → action selection → automation pipeline.
        
        Args:
            max_duration_seconds: Maximum episode duration (None = no limit)
            
        Returns:
            Completed session object
            
        Raises:
            RuntimeError: If episode fails to start
        """
        # Initialize session
        session = self._start_session()
        episode_start = time.time()
        
        logger.info(
            "episode_started",
            session_id=session.session_id,
            episode_number=self.episode_count
        )
        
        try:
            # Main episode loop
            while True:
                # Check termination conditions
                if self._should_terminate_episode(session, episode_start, max_duration_seconds):
                    break
                
                # Execute one step of the perception-action loop
                step_result = self._execute_step(session)
                
                if not step_result:
                    # Step failed, but continue (agent is learning)
                    continue
                
                # Small delay between actions (prevent spamming)
                wait(0.5)
            
            # End session
            self._end_session(session, EndCondition.TIMEOUT)
            
        except KeyboardInterrupt:
            logger.info("episode_interrupted", session_id=session.session_id)
            self._end_session(session, EndCondition.MANUAL_STOP)
            raise
        
        except Exception as e:
            logger.error(
                "episode_error",
                session_id=session.session_id,
                error=str(e),
                exc_info=True
            )
            self._end_session(session, EndCondition.CRASH)
            raise
        
        return session
    
    def _execute_step(self, session: Session) -> bool:
        """
        Execute one step of the perception-action loop.
        
        T107: Integrated pipeline.
        
        Returns:
            True if step succeeded, False otherwise
        """
        step_start = time.time()
        
        try:
            # 1. VISION: Capture game state
            logger.debug("step_vision_start")
            game_state = capture_game_state(self.window_name)
            
            if not game_state:
                logger.warning("vision_failed", reason="no_game_state")
                return False
            
            # 2. NLP: Analyze narrative text (if any)
            logger.debug("step_nlp_start")
            narrative_goals = []
            if game_state.text_regions:
                # Combine all text regions
                narrative_text = " ".join([tr.text for tr in game_state.text_regions])
                narrative_goals = extract_goals(narrative_text)
                
                if narrative_goals:
                    logger.debug(
                        "goals_extracted",
                        count=len(narrative_goals),
                        goals=[g.goal_type.value for g in narrative_goals]
                    )
            
            # 3. LEARNING: Select action
            logger.debug("step_learning_start")
            try:
                action = select_action(game_state)
            except ModelNotLoadedError:
                # RL model not trained yet, use fallback
                action = self._fallback_action_selection(game_state)
            
            if not action:
                logger.warning("action_selection_failed")
                return False
            
            # 4. SAFETY: Validate action
            logger.debug("step_safety_start", action_type=action.action_type.value)
            
            # Build context for safety validation
            context = {
                "window_bounds": game_state.window_bounds,
                "window_focused": True,  # TODO: Actual focus check
                "recent_actions": self.action_history[-10:] if self.action_history else []
            }
            
            validation_result = validate_action(
                action=action,
                context=context
            )
            
            if not validation_result.is_allowed:
                logger.warning(
                    "action_rejected",
                    action_type=action.action_type.value,
                    reason=validation_result.reason
                )
                self.metrics['failed_actions'] += 1
                return False
            
            # 5. AUTOMATION: Execute action
            logger.debug("step_automation_start", action_type=action.action_type.value)
            execution_success = self._execute_action(action)
            
            if not execution_success:
                self.metrics['failed_actions'] += 1
                return False
            
            # 6. RECORD: Update knowledge and history
            self.action_history.append(action)
            session.total_actions += 1
            self.metrics['successful_actions'] += 1
            self.metrics['total_actions'] += 1
            
            # 7. LOOP DETECTION: Check for repetitive behavior
            if len(self.action_history) >= self.loop_detection_window:
                is_looping = detect_loop(
                    self.action_history,
                    window_size=self.loop_detection_window
                )
                
                if is_looping:
                    logger.warning(
                        "loop_detected",
                        session_id=session.session_id,
                        actions=session.total_actions
                    )
                    self.metrics['loops_detected'] += 1
                    # TODO: Implement loop-breaking strategy
            
            step_duration = (time.time() - step_start) * 1000
            logger.debug(
                "step_completed",
                duration_ms=step_duration,
                total_actions=session.total_actions
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "step_error",
                error=str(e),
                exc_info=True
            )
            return False
    
    def _execute_action(self, action: Action) -> bool:
        """
        Execute action using automation library.
        
        Returns:
            True if execution succeeded, False otherwise
        """
        try:
            if action.action_type == ActionType.CLICK:
                point = action.parameters.get('point')
                if point:
                    simulate_click(
                        point=point,
                        button=action.parameters.get('button', 'left')
                    )
                    return True
                else:
                    logger.warning("click_missing_point")
                    return False
            
            elif action.action_type == ActionType.KEY_PRESS:
                key = action.parameters.get('key')
                if key:
                    simulate_key_press(
                        key=key,
                        modifiers=action.parameters.get('modifiers', [])
                    )
                    return True
                else:
                    logger.warning("key_press_missing_key")
                    return False
            
            elif action.action_type == ActionType.WAIT:
                wait(action.parameters.get('duration', 1.0))
                return True
            
            else:
                logger.warning("unsupported_action_type", action_type=action.action_type)
                return False
        
        except (OutOfBoundsError, BlacklistedKeyError, WindowNotFocusedError) as e:
            logger.warning(
                "action_execution_blocked",
                action_type=action.action_type.value,
                reason=str(e)
            )
            return False
        
        except Exception as e:
            logger.error(
                "action_execution_error",
                action_type=action.action_type.value,
                error=str(e)
            )
            return False
    
    def _fallback_action_selection(self, game_state: GameState) -> Optional[Action]:
        """
        Fallback action selection when RL model is not available.
        
        Simple rule-based approach:
        - Click on detected elements
        - Wait if no elements detected
        
        Returns:
            Action to execute
        """
        # If elements detected, click on first one
        if game_state.elements:
            element = game_state.elements[0]
            
            return Action(
                action_type=ActionType.CLICK,
                parameters={
                    'point': element.center,
                    'button': 'left'
                },
                timestamp=datetime.now()
            )
        
        # Otherwise, wait
        return Action(
            action_type=ActionType.WAIT,
            parameters={'duration': 1.0},
            timestamp=datetime.now()
        )
    
    def _should_terminate_episode(
        self,
        session: Session,
        episode_start: float,
        max_duration_seconds: Optional[float]
    ) -> bool:
        """
        Check if episode should terminate.
        
        Termination conditions:
        - Max actions reached
        - Max duration exceeded
        - Game over detected (future)
        - Victory detected (future)
        """
        # Max actions
        if session.total_actions >= self.max_actions_per_episode:
            logger.info(
                "max_actions_reached",
                session_id=session.session_id,
                actions=session.total_actions
            )
            return True
        
        # Max duration
        if max_duration_seconds:
            elapsed = time.time() - episode_start
            if elapsed >= max_duration_seconds:
                logger.info(
                    "max_duration_reached",
                    session_id=session.session_id,
                    duration=elapsed
                )
                return True
        
        return False
    
    def _start_session(self) -> Session:
        """Create and initialize a new session."""
        session_id = self._generate_session_id()
        
        session = Session(
            session_id=session_id,
            agent_id=self.agent_id,
            start_time=datetime.now(),
            total_actions=0,
            total_reward=0.0
        )
        
        self.current_session = session
        self.action_history = []
        self.episode_count += 1
        
        return session
    
    def _end_session(self, session: Session, end_condition: EndCondition):
        """
        End session and persist.
        
        T108: Session recording and persistence.
        """
        session.end_time = datetime.now()
        session.end_condition = end_condition
        
        # Store session
        try:
            store_session(session)
            logger.info(
                "session_stored",
                session_id=session.session_id,
                actions=session.total_actions,
                duration=session.duration_seconds
            )
        except Exception as e:
            logger.error(
                "session_storage_failed",
                session_id=session.session_id,
                error=str(e)
            )
        
        # Update metrics
        self.metrics['episodes_completed'] += 1
        self._update_average_episode_length(session.total_actions)
        
        self.current_session = None
    
    def _update_average_episode_length(self, episode_length: int):
        """Update running average of episode length."""
        n = self.metrics['episodes_completed']
        current_avg = self.metrics['average_episode_length']
        
        # Incremental average: avg_n = avg_(n-1) + (x_n - avg_(n-1)) / n
        new_avg = current_avg + (episode_length - current_avg) / n
        self.metrics['average_episode_length'] = new_avg
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        unique_str = f"{self.agent_id}_{datetime.now().isoformat()}_{self.episode_count}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics.
        
        T110: Real-time metrics tracking.
        
        Returns:
            Dictionary of metrics
        """
        success_rate = 0.0
        if self.metrics['total_actions'] > 0:
            success_rate = self.metrics['successful_actions'] / self.metrics['total_actions']
        
        return {
            **self.metrics,
            'success_rate': success_rate,
            'current_episode': self.episode_count,
        }
    
    def articulate_strategy(self) -> str:
        """
        Generate human-readable description of current strategy.
        
        T111: Articulate strategy for human understanding.
        
        Returns:
            Natural language strategy description
        """
        metrics = self.get_metrics()
        
        strategy = f"""
Agent Strategy Summary (ID: {self.agent_id})
{'=' * 50}

Performance:
- Episodes Completed: {metrics['episodes_completed']}
- Total Actions: {metrics['total_actions']}
- Success Rate: {metrics['success_rate']:.1%}
- Average Episode Length: {metrics['average_episode_length']:.1f} actions

Behavior Patterns:
- Loops Detected: {metrics['loops_detected']}
- Failed Actions: {metrics['failed_actions']}

Current Approach:
"""
        
        if metrics['total_actions'] == 0:
            strategy += "- Just starting, gathering initial experience\n"
        elif metrics['loops_detected'] > 5:
            strategy += "- Experiencing repetitive behavior, needs strategy adjustment\n"
        elif metrics['success_rate'] > 0.8:
            strategy += "- Performing well, actions mostly successful\n"
        else:
            strategy += "- Learning phase, experimenting with different actions\n"
        
        return strategy.strip()


class TrainingRunner:
    """
    Runs multiple training episodes for agent learning.
    
    T109: Training loop implementation.
    """
    
    def __init__(self, agent_runner: AgentRunner):
        """
        Initialize training runner.
        
        Args:
            agent_runner: AgentRunner instance to train
        """
        self.agent_runner = agent_runner
        self.training_sessions: List[Session] = []
        
        logger.info("training_runner_initialized", agent_id=agent_runner.agent_id)
    
    def train(
        self,
        num_episodes: int = 100,
        max_episode_duration: Optional[float] = 300.0,
        checkpoint_interval: int = 10
    ) -> List[Session]:
        """
        Run training episodes.
        
        Args:
            num_episodes: Number of episodes to run
            max_episode_duration: Maximum seconds per episode
            checkpoint_interval: Save checkpoint every N episodes
            
        Returns:
            List of completed sessions
        """
        logger.info(
            "training_started",
            num_episodes=num_episodes,
            max_duration=max_episode_duration
        )
        
        for episode_num in range(1, num_episodes + 1):
            logger.info(
                "training_episode_start",
                episode=episode_num,
                total=num_episodes
            )
            
            try:
                # Run episode
                session = self.agent_runner.run_episode(
                    max_duration_seconds=max_episode_duration
                )
                self.training_sessions.append(session)
                
                # Log progress
                metrics = self.agent_runner.get_metrics()
                logger.info(
                    "training_episode_complete",
                    episode=episode_num,
                    actions=session.total_actions,
                    success_rate=metrics['success_rate']
                )
                
                # Checkpoint
                if episode_num % checkpoint_interval == 0:
                    self._save_checkpoint(episode_num)
            
            except KeyboardInterrupt:
                logger.info("training_interrupted", completed_episodes=episode_num - 1)
                break
            
            except Exception as e:
                logger.error(
                    "training_episode_error",
                    episode=episode_num,
                    error=str(e),
                    exc_info=True
                )
                # Continue with next episode
                continue
        
        logger.info(
            "training_completed",
            episodes=len(self.training_sessions),
            total_actions=self.agent_runner.metrics['total_actions']
        )
        
        return self.training_sessions
    
    def _save_checkpoint(self, episode_num: int):
        """
        Save training checkpoint.
        
        T112: Crash recovery and resume logic.
        """
        checkpoint_dir = Path("data/checkpoints")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"checkpoint_ep{episode_num}.txt"
        
        try:
            with open(checkpoint_file, 'w') as f:
                f.write(f"Episode: {episode_num}\n")
                f.write(f"Sessions: {len(self.training_sessions)}\n")
                f.write(f"Total Actions: {self.agent_runner.metrics['total_actions']}\n")
                f.write(f"\nMetrics:\n")
                for key, value in self.agent_runner.get_metrics().items():
                    f.write(f"  {key}: {value}\n")
            
            logger.info("checkpoint_saved", episode=episode_num, file=str(checkpoint_file))
        
        except Exception as e:
            logger.error("checkpoint_save_failed", episode=episode_num, error=str(e))
