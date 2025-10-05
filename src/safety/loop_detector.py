"""
Loop Detection Module

Detects repetitive action patterns that indicate unproductive loops.
Uses sliding window analysis and Levenshtein distance for pattern matching.
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from collections import deque
import Levenshtein

from src.lib.types import Action


class LoopDetector:
    """
    Detects when the agent enters unproductive loops of repeated actions.
    
    Uses a sliding window approach to track recent actions and identifies
    when the same sequence of actions repeats 3+ times within a 5-minute window.
    """
    
    def __init__(
        self,
        window_duration: timedelta = timedelta(minutes=5),
        min_sequence_length: int = 2,
        min_repetitions: int = 3,
        similarity_threshold: float = 0.8
    ):
        """
        Initialize loop detector.
        
        Args:
            window_duration: Time window to analyze (default 5 minutes)
            min_sequence_length: Minimum actions in a pattern (default 2)
            min_repetitions: How many times pattern must repeat (default 3)
            similarity_threshold: Levenshtein similarity threshold 0-1 (default 0.8)
        """
        self.window_duration = window_duration
        self.min_sequence_length = min_sequence_length
        self.min_repetitions = min_repetitions
        self.similarity_threshold = similarity_threshold
        
        # Sliding window of recent actions
        self.action_window: deque = deque()
        
    def add_action(self, action: Action) -> None:
        """
        Add an action to the sliding window.
        
        Args:
            action: The action that was executed
        """
        self.action_window.append(action)
        self._cleanup_old_actions()
        
    def _cleanup_old_actions(self) -> None:
        """Remove actions outside the time window."""
        if not self.action_window:
            return
            
        cutoff_time = datetime.now() - self.window_duration
        
        while self.action_window and self.action_window[0].timestamp < cutoff_time:
            self.action_window.popleft()
    
    def detect_loop(self) -> Tuple[bool, Optional[str]]:
        """
        Detect if actions form a repetitive loop.
        
        Returns:
            Tuple of (is_loop_detected, pattern_description)
            If no loop: (False, None)
            If loop: (True, "pattern description")
        """
        self._cleanup_old_actions()
        
        if len(self.action_window) < self.min_sequence_length * self.min_repetitions:
            return False, None
        
        # Convert actions to sequence strings for pattern matching
        action_sequence = [self._action_to_string(a) for a in self.action_window]
        
        # Try different sequence lengths
        for seq_len in range(self.min_sequence_length, len(action_sequence) // self.min_repetitions + 1):
            if self._has_repeating_pattern(action_sequence, seq_len):
                pattern = " → ".join(action_sequence[-seq_len:])
                return True, f"Repeating pattern detected ({self.min_repetitions}+ times): {pattern}"
        
        return False, None
    
    def _action_to_string(self, action: Action) -> str:
        """
        Convert action to a string representation for pattern matching.
        
        Args:
            action: The action to convert
            
        Returns:
            String representation (e.g., "click(100,200)", "drag(50,50→100,100)")
        """
        action_type = action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)
        params = action.parameters
        
        if action_type == "click":
            return f"click({params.get('x', 0)},{params.get('y', 0)})"
        elif action_type == "drag":
            start = params.get('start', {})
            end = params.get('end', {})
            return f"drag({start.get('x', 0)},{start.get('y', 0)}→{end.get('x', 0)},{end.get('y', 0)})"
        elif action_type == "key_press":
            return f"key({params.get('key', '')})"
        elif action_type == "wait":
            return f"wait({params.get('duration', 0):.1f}s)"
        else:
            return f"{action_type}(...)"
    
    def _has_repeating_pattern(self, sequence: List[str], pattern_length: int) -> bool:
        """
        Check if a pattern of given length repeats min_repetitions times.
        
        Uses Levenshtein distance to allow for slight variations in repetitions.
        
        Args:
            sequence: List of action strings
            pattern_length: Length of pattern to look for
            
        Returns:
            True if pattern repeats min_repetitions times
        """
        if len(sequence) < pattern_length * self.min_repetitions:
            return False
        
        # Extract candidate pattern (most recent occurrence)
        pattern = sequence[-pattern_length:]
        pattern_str = "|".join(pattern)
        
        # Count how many times this pattern appears (with similarity matching)
        repetition_count = 0
        
        for i in range(len(sequence) - pattern_length, -1, -pattern_length):
            candidate = sequence[i:i + pattern_length]
            candidate_str = "|".join(candidate)
            
            similarity = self._calculate_similarity(pattern_str, candidate_str)
            
            if similarity >= self.similarity_threshold:
                repetition_count += 1
            else:
                break  # Pattern broke
        
        return repetition_count >= self.min_repetitions
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using Levenshtein distance.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score from 0.0 (completely different) to 1.0 (identical)
        """
        if not str1 or not str2:
            return 0.0
        
        distance = Levenshtein.distance(str1, str2)
        max_len = max(len(str1), len(str2))
        
        if max_len == 0:
            return 1.0
        
        return 1.0 - (distance / max_len)
    
    def reset(self) -> None:
        """Clear the action window."""
        self.action_window.clear()
    
    def get_recent_actions(self, count: int = 10) -> List[Action]:
        """
        Get the most recent N actions from the window.
        
        Args:
            count: Number of recent actions to return
            
        Returns:
            List of recent actions (newest last)
        """
        self._cleanup_old_actions()
        return list(self.action_window)[-count:]
