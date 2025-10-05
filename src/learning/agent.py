"""
Reinforcement Learning Agent Module

Implements PPO agent using Stable-Baselines3 and custom Gym environment
for Cultist Simulator gameplay.
"""

from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv
import torch

from src.lib.types import GameState, Action, ActionType, Point, Rect
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class CultistSimulatorEnv(gym.Env):
    """
    Custom Gym environment for Cultist Simulator.
    
    Observation Space: 
        - Flattened vector representation of game state
        - Includes: element positions, resources, card states, narrative embeddings
    
    Action Space:
        - Discrete actions: click at grid position, drag card, wait, etc.
        - Mapped to actual game interactions through automation library
    
    Reward:
        - Sparse rewards for achieving goals (win condition, survival milestones)
        - Small penalties for failures and time passage
        - Shaped rewards for progress (new discoveries, resource gains)
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}
    
    def __init__(
        self,
        vision_lib=None,
        automation_lib=None,
        nlp_lib=None,
        safety_lib=None,
        max_steps: int = 1000,
        grid_resolution: Tuple[int, int] = (10, 10),
        render_mode: Optional[str] = None
    ):
        """
        Initialize the Cultist Simulator Gym environment.
        
        Args:
            vision_lib: Vision library for game state capture
            automation_lib: Automation library for action execution
            nlp_lib: NLP library for narrative understanding
            safety_lib: Safety library for action validation
            max_steps: Maximum steps per episode
            grid_resolution: Grid size for click positions (10x10 = 100 positions)
            render_mode: Rendering mode (None, "human", or "rgb_array")
        """
        super().__init__()
        
        self.vision_lib = vision_lib
        self.automation_lib = automation_lib
        self.nlp_lib = nlp_lib
        self.safety_lib = safety_lib
        self.max_steps = max_steps
        self.grid_resolution = grid_resolution
        self.render_mode = render_mode
        
        # State tracking
        self.current_state: Optional[GameState] = None
        self.step_count: int = 0
        self.total_reward: float = 0.0
        self.episode_start_time: Optional[float] = None
        
        # Define observation space
        # Components: grid elements (100), resources (10), card states (50), 
        # narrative embedding (384), misc (6) = 550 dimensions
        obs_dim = (grid_resolution[0] * grid_resolution[1]) + 10 + 50 + 384 + 6
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(obs_dim,),
            dtype=np.float32
        )
        
        # Define action space
        # Action types: click (100 grid positions) + drag (100x100) + wait (1) + special (10)
        # Simplified: 100 click positions + 10 special actions = 110 discrete actions
        self.action_space = spaces.Discrete(110)
        
        logger.info(
            f"Initialized CultistSimulatorEnv with obs_space={self.observation_space.shape}, "
            f"action_space={self.action_space.n}"
        )
    
    def reset(
        self, 
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment to initial state.
        
        Args:
            seed: Random seed for reproducibility
            options: Additional options
            
        Returns:
            Tuple of (observation, info_dict)
        """
        super().reset(seed=seed)
        
        self.step_count = 0
        self.total_reward = 0.0
        
        # Capture initial game state
        if self.vision_lib:
            self.current_state = self.vision_lib.capture_game_state()
        else:
            # Mock state for testing
            self.current_state = self._create_mock_state()
        
        observation = self._state_to_observation(self.current_state)
        info = {
            "step": self.step_count,
            "total_reward": self.total_reward,
            "game_state": str(self.current_state) if self.current_state else None
        }
        
        logger.info(f"Environment reset - episode starting")
        return observation, info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        
        Args:
            action: Integer action from action space
            
        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        self.step_count += 1
        
        # Convert action integer to actual game action
        game_action = self._action_to_game_action(action)
        
        # Execute action through automation library
        if self.automation_lib and self.safety_lib:
            # Validate action
            validation = self.safety_lib.validate_action(game_action)
            
            if validation.is_valid:
                # Execute action
                execution_result = self.automation_lib.execute_action(game_action)
            else:
                logger.warning(f"Action blocked by safety: {validation.reason}")
                execution_result = None
        else:
            execution_result = None
        
        # Capture new game state
        previous_state = self.current_state
        if self.vision_lib:
            self.current_state = self.vision_lib.capture_game_state()
        else:
            self.current_state = self._create_mock_state()
        
        # Calculate reward
        reward = self._calculate_reward(previous_state, self.current_state, game_action)
        self.total_reward += reward
        
        # Check termination conditions
        terminated = self._is_terminated(self.current_state)
        truncated = self.step_count >= self.max_steps
        
        # Create observation
        observation = self._state_to_observation(self.current_state)
        
        info = {
            "step": self.step_count,
            "total_reward": self.total_reward,
            "action_executed": game_action.action_type if game_action else None,
            "reward_breakdown": self._get_reward_breakdown(previous_state, self.current_state),
            "game_state": str(self.current_state) if self.current_state else None
        }
        
        return observation, reward, terminated, truncated, info
    
    def _action_to_game_action(self, action: int) -> Action:
        """
        Convert discrete action integer to game Action object.
        
        Args:
            action: Integer from action space (0-109)
            
        Returns:
            Action object to execute
        """
        from datetime import datetime
        
        if action < 100:
            # Click action (0-99)
            grid_x = action % self.grid_resolution[0]
            grid_y = action // self.grid_resolution[0]
            
            # Convert grid position to screen coordinates
            # Assuming 1280x720 window (will be replaced by actual window bounds)
            screen_x = int((grid_x + 0.5) * 1280 / self.grid_resolution[0])
            screen_y = int((grid_y + 0.5) * 720 / self.grid_resolution[1])
            
            return Action(
                action_type=ActionType.CLICK,
                parameters={"x": screen_x, "y": screen_y, "button": "left"},
                timestamp=datetime.now()
            )
        
        elif action == 100:
            # Wait action
            return Action(
                action_type=ActionType.WAIT,
                parameters={"duration": 1.0},
                timestamp=datetime.now()
            )
        
        else:
            # Special actions (101-109) - to be defined based on game mechanics
            # For now, default to wait
            return Action(
                action_type=ActionType.WAIT,
                parameters={"duration": 0.5},
                timestamp=datetime.now()
            )
    
    def _state_to_observation(self, state: Optional[GameState]) -> np.ndarray:
        """
        Convert GameState to observation vector.
        
        Args:
            state: Current game state
            
        Returns:
            Numpy array observation
        """
        if state is None or self.observation_space.shape is None:
            # Return zero observation
            obs_shape = self.observation_space.shape if self.observation_space.shape else (550,)
            return np.zeros(obs_shape, dtype=np.float32)
        
        observation_parts = []
        
        # 1. Grid element presence (100 dimensions)
        grid = np.zeros((self.grid_resolution[0], self.grid_resolution[1]), dtype=np.float32)
        if state.elements:
            for element in state.elements:
                if element.bounds:
                    # Map element to grid cell
                    center_x = element.bounds.x + element.bounds.width / 2
                    center_y = element.bounds.y + element.bounds.height / 2
                    grid_x = int(center_x * self.grid_resolution[0] / 1280)
                    grid_y = int(center_y * self.grid_resolution[1] / 720)
                    if 0 <= grid_x < self.grid_resolution[0] and 0 <= grid_y < self.grid_resolution[1]:
                        grid[grid_y, grid_x] = 1.0
        observation_parts.append(grid.flatten())
        
        # 2. Resources (10 dimensions) - normalized
        # Extract from metadata if available
        resources = np.zeros(10, dtype=np.float32)
        if state.metadata and "resources" in state.metadata:
            resource_dict = state.metadata["resources"]
            for i, (key, value) in enumerate(list(resource_dict.items())[:10]):
                resources[i] = min(float(value) / 100.0, 1.0)  # Normalize
        observation_parts.append(resources)
        
        # 3. Card states (50 dimensions)
        # Extract from metadata if available
        card_states = np.zeros(50, dtype=np.float32)
        if state.metadata and "cards" in state.metadata:
            cards = state.metadata["cards"]
            for i, card in enumerate(cards[:50]):
                card_states[i] = 1.0 if card.get("state") == "active" else 0.5
        observation_parts.append(card_states)
        
        # 4. Narrative embedding (384 dimensions from sentence-transformers)
        narrative_embedding = np.zeros(384, dtype=np.float32)
        if state.text_regions and self.nlp_lib:
            # Combine narrative texts
            narrative = " ".join([tr.text for tr in state.text_regions[:3]])
            if narrative:
                try:
                    analysis = self.nlp_lib.analyze_text(narrative)
                    if analysis and "embedding" in analysis:
                        narrative_embedding = np.array(analysis["embedding"], dtype=np.float32)
                except Exception as e:
                    logger.warning(f"Failed to analyze narrative: {e}")
        observation_parts.append(narrative_embedding)
        
        # 5. Miscellaneous (6 dimensions)
        has_focus = state.metadata.get("has_focus", True) if state.metadata else True
        is_game_over = state.metadata.get("is_game_over", False) if state.metadata else False
        is_win = state.metadata.get("is_win_state", False) if state.metadata else False
        
        misc = np.array([
            1.0 if has_focus else 0.0,
            1.0 if is_game_over else 0.0,
            1.0 if is_win else 0.0,
            len(state.elements) / 100.0 if state.elements else 0.0,
            len(state.text_regions) / 50.0 if state.text_regions else 0.0,
            self.step_count / self.max_steps
        ], dtype=np.float32)
        observation_parts.append(misc)
        
        # Concatenate all parts
        observation = np.concatenate(observation_parts)
        
        return observation
    
    def _calculate_reward(
        self,
        prev_state: Optional[GameState],
        curr_state: Optional[GameState],
        action: Action
    ) -> float:
        """
        Calculate reward for the transition.
        
        Reward structure:
        - Win condition: +1000
        - Survival: +1 per step
        - New discoveries: +10
        - Resource gains: +0.1 per unit
        - Game over: -100
        - Blocked action: -1
        
        Args:
            prev_state: Previous game state
            curr_state: Current game state
            action: Action taken
            
        Returns:
            Reward value
        """
        if curr_state is None:
            return -10.0  # Penalty for invalid state
        
        reward = 0.0
        
        # Check metadata for game status
        is_win = curr_state.metadata.get("is_win_state", False) if curr_state.metadata else False
        is_game_over = curr_state.metadata.get("is_game_over", False) if curr_state.metadata else False
        
        # Win condition
        if is_win:
            reward += 1000.0
            logger.info("Win condition detected! +1000 reward")
        
        # Game over penalty
        elif is_game_over:
            reward -= 100.0
            logger.info("Game over detected. -100 reward")
        
        # Survival reward (small positive reward for each step)
        else:
            reward += 1.0
        
        # Resource changes (from metadata)
        if prev_state and prev_state.metadata and curr_state.metadata:
            prev_resources = prev_state.metadata.get("resources", {})
            curr_resources = curr_state.metadata.get("resources", {})
            for key in curr_resources:
                if key in prev_resources:
                    delta = float(curr_resources[key]) - float(prev_resources[key])
                    reward += delta * 0.1
        
        # New element discoveries
        if prev_state and curr_state.elements:
            new_elements = len(curr_state.elements) - (
                len(prev_state.elements) if prev_state.elements else 0
            )
            if new_elements > 0:
                reward += new_elements * 10.0
        
        # Blocked action penalty (check metadata)
        if action.metadata and action.metadata.get("was_blocked", False):
            reward -= 1.0
        
        return reward
    
    def _is_terminated(self, state: Optional[GameState]) -> bool:
        """Check if episode should terminate."""
        if state is None:
            return True
        
        # Check metadata for termination conditions
        is_game_over = state.metadata.get("is_game_over", False) if state.metadata else False
        is_win = state.metadata.get("is_win_state", False) if state.metadata else False
        
        # Terminate on win or game over
        if is_game_over or is_win:
            return True
        
        return False
    
    def _get_reward_breakdown(
        self,
        prev_state: Optional[GameState],
        curr_state: Optional[GameState]
    ) -> Dict[str, float]:
        """Get detailed reward breakdown for logging."""
        is_game_over = False
        is_win = False
        
        if curr_state and curr_state.metadata:
            is_game_over = curr_state.metadata.get("is_game_over", False)
            is_win = curr_state.metadata.get("is_win_state", False)
        
        breakdown = {
            "survival": 1.0 if curr_state and not is_game_over else 0.0,
            "win_bonus": 1000.0 if is_win else 0.0,
            "game_over_penalty": -100.0 if is_game_over else 0.0,
            "resource_delta": 0.0,
            "discovery_bonus": 0.0
        }
        return breakdown
    
    def _create_mock_state(self) -> GameState:
        """Create a mock game state for testing without actual game."""
        from datetime import datetime
        
        return GameState(
            timestamp=datetime.now(),
            window_bounds=Rect(x=0, y=0, width=1280, height=720),
            elements=[],
            text_regions=[],
            screenshot=None,
            metadata={
                "has_focus": True,
                "is_game_over": False,
                "is_win_state": False,
                "resources": {},
                "cards": []
            }
        )
    
    def render(self):
        """Render the environment (optional)."""
        if self.render_mode == "human":
            logger.info(f"Step {self.step_count}: Reward={self.total_reward:.2f}")
        elif self.render_mode == "rgb_array":
            # Return screenshot as numpy array
            if self.current_state and self.current_state.screenshot is not None:
                return self.current_state.screenshot
        return None
    
    def close(self):
        """Clean up resources."""
        logger.info("Closing Cultist Simulator environment")
        super().close()


class PPOAgent:
    """
    PPO-based RL agent for Cultist Simulator.
    
    Wraps Stable-Baselines3 PPO with custom training and evaluation logic.
    """
    
    def __init__(
        self,
        env: CultistSimulatorEnv,
        learning_rate: float = 3e-4,
        n_steps: int = 2048,
        batch_size: int = 64,
        n_epochs: int = 10,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_range: float = 0.2,
        ent_coef: float = 0.01,
        device: str = "auto"
    ):
        """
        Initialize PPO agent.
        
        Args:
            env: Cultist Simulator gym environment
            learning_rate: Learning rate for optimizer
            n_steps: Number of steps to run per environment per update
            batch_size: Minibatch size
            n_epochs: Number of epochs for optimization
            gamma: Discount factor
            gae_lambda: GAE lambda parameter
            clip_range: PPO clipping parameter
            ent_coef: Entropy coefficient (for exploration)
            device: Device to run on ("auto", "cpu", or "cuda")
        """
        self.env = env
        
        # Create vectorized environment (required by SB3)
        vec_env = DummyVecEnv([lambda: env])
        
        # Initialize PPO model
        self.model = PPO(
            policy="MlpPolicy",
            env=vec_env,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            gae_lambda=gae_lambda,
            clip_range=clip_range,
            ent_coef=ent_coef,
            verbose=1,
            device=device,
            tensorboard_log="./data/logs/tensorboard/"
        )
        
        logger.info(
            f"Initialized PPO agent with lr={learning_rate}, "
            f"entropy_coef={ent_coef} (exploration/exploitation balance)"
        )
    
    def train(
        self,
        total_timesteps: int,
        callback: Optional[BaseCallback] = None
    ) -> None:
        """
        Train the agent.
        
        Args:
            total_timesteps: Total number of timesteps to train
            callback: Optional callback for logging/checkpointing
        """
        logger.info(f"Starting training for {total_timesteps} timesteps")
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            progress_bar=True
        )
        logger.info("Training complete")
    
    def predict(
        self,
        observation: np.ndarray,
        deterministic: bool = False
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Predict action for given observation.
        
        Args:
            observation: Current observation
            deterministic: If True, use deterministic policy (no exploration)
            
        Returns:
            Tuple of (action, state) where state is for recurrent policies
        """
        action, state = self.model.predict(observation, deterministic=deterministic)
        return action, state
    
    def save(self, path: str) -> None:
        """Save the model to disk."""
        self.model.save(path)
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str) -> None:
        """Load the model from disk."""
        self.model = PPO.load(path, env=self.model.get_env())
        logger.info(f"Model loaded from {path}")
