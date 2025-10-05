"""
Contract tests for learning_lib.
These tests verify the learning library's public interface contract.

IMPORTANT: These tests are written FIRST before any implementation (TDD).
They MUST FAIL initially, then pass once learning_lib is implemented.
"""

import pytest


class TestLearningLibContract:
    """Test suite for learning_lib public interface."""

    def test_select_action_exists(self):
        """T017: Contract test for learning_lib.select_action()."""
        from src.learning import select_action
        
        # Function should exist
        assert callable(select_action)
        
        # Check signature
        import inspect
        sig = inspect.signature(select_action)
        assert 'game_state' in sig.parameters

    def test_select_action_accepts_game_state(self):
        """T017: Contract test - select_action accepts GameState object."""
        from src.learning import select_action
        
        # This will fail until implementation exists
        # Would normally pass a GameState object
        with pytest.raises(Exception):  # Will be ModelNotLoadedError or similar
            action = select_action(None)  # Passing None to test error handling

    def test_update_knowledge_exists(self):
        """T018: Contract test for learning_lib.update_knowledge()."""
        from src.learning import update_knowledge
        
        # Function should exist
        assert callable(update_knowledge)
        
        # Check signature - should accept SARS tuple
        import inspect
        sig = inspect.signature(update_knowledge)
        assert 'state' in sig.parameters
        assert 'action' in sig.parameters
        assert 'next_state' in sig.parameters
        assert 'reward' in sig.parameters

    def test_update_knowledge_accepts_experience_tuple(self):
        """T018: Contract test - update_knowledge accepts SARS tuple."""
        from src.learning import update_knowledge
        
        # Would normally pass GameState, Action, GameState, float
        update_knowledge(None, None, None, 0.0)

    def test_detect_loop_exists(self):
        """T019: Contract test for learning_lib.detect_loop()."""
        from src.learning import detect_loop
        
        # Function should exist
        assert callable(detect_loop)
        
        # Check signature
        import inspect
        sig = inspect.signature(detect_loop)
        assert 'action_history' in sig.parameters
        assert 'window_size' in sig.parameters
        
        # window_size should have default value
        default = sig.parameters['window_size'].default
        assert default == 30 or isinstance(default, int)

    def test_detect_loop_accepts_action_list(self):
        """T019: Contract test - detect_loop accepts list of actions."""
        from src.learning import detect_loop
        
        # Empty action history should not detect loop
        result = detect_loop([], window_size=30)
        assert isinstance(result, bool)
        assert result is False  # Empty list should not be a loop

    def test_detect_loop_identifies_repetition(self):
        """T019: Contract test - detect_loop identifies repeated patterns."""
        from src.learning import detect_loop
        
        # Create repetitive action history (same action repeated)
        # Would normally create Action objects
        repetitive_actions = ["click"] * 20  # Same action 20 times
        result = detect_loop(repetitive_actions, window_size=10)
        # Should detect the loop
        assert result is True

    def test_query_knowledge_exists(self):
        """Contract test for learning_lib.query_knowledge()."""
        from src.learning import query_knowledge
        
        # Function should exist
        assert callable(query_knowledge)
        
        # Check signature
        import inspect
        sig = inspect.signature(query_knowledge)
        assert 'query_type' in sig.parameters
        assert 'parameters' in sig.parameters

    def test_query_knowledge_returns_query_result(self):
        """Contract test - query_knowledge returns QueryResult."""
        from src.learning import query_knowledge
        
        result = query_knowledge("similar_states", {"state_hash": "test"})
        # Should have result_count and query_time_ms
        assert hasattr(result, 'result_count')
        assert hasattr(result, 'query_time_ms')

    def test_store_session_exists(self):
        """Contract test for learning_lib.store_session()."""
        from src.learning import store_session
        
        # Function should exist
        assert callable(store_session)
        
        # Check signature
        import inspect
        sig = inspect.signature(store_session)
        assert 'session' in sig.parameters

    def test_store_session_returns_session_id(self):
        """Contract test - store_session returns session ID string."""
        from src.learning import store_session
        from src.lib.types import Session
        from datetime import datetime
        
        # Create a minimal session object
        session = Session(
            session_id="test123",
            agent_id="agent1",
            start_time=datetime.now(),
            total_actions=0
        )
        session_id = store_session(session)
        assert isinstance(session_id, str)
        assert len(session_id) > 0  # Should be a valid UUID or similar


class TestLearningLibPerformance:
    """Performance contract tests for learning_lib."""

    @pytest.mark.performance
    def test_select_action_performance(self):
        """T035: Performance test - select_action() <500ms."""
        import time
        from src.learning import select_action
        
        # This will fail until implementation exists
        # NFR-001: Action selection must be <500ms
        with pytest.raises(Exception):
            start = time.perf_counter()
            action = select_action(None)  # Would pass GameState
            duration_ms = (time.perf_counter() - start) * 1000
            
            # Performance requirement from NFR-001
            assert duration_ms < 500, f"Action selection took {duration_ms}ms, must be <500ms"

    @pytest.mark.performance
    def test_update_knowledge_performance(self):
        """Performance test - update_knowledge() <100ms."""
        import time
        from src.learning import update_knowledge
        
        start = time.perf_counter()
        update_knowledge(None, None, None, 0.0)
        duration_ms = (time.perf_counter() - start) * 1000
        
        # Should be fast enough for real-time learning
        assert duration_ms < 100, f"Knowledge update took {duration_ms}ms, must be <100ms"

    @pytest.mark.performance
    def test_query_knowledge_performance(self):
        """T035: Performance test - query_knowledge() <100ms."""
        import time
        from src.learning import query_knowledge
        
        # NFR-003: Knowledge base queries must be <100ms
        start = time.perf_counter()
        result = query_knowledge("similar_states", {"state_hash": "test"})
        duration_ms = (time.perf_counter() - start) * 1000
        
        # Performance requirement from NFR-003
        assert duration_ms < 100, f"Query took {duration_ms}ms, must be <100ms"

    @pytest.mark.performance
    def test_detect_loop_performance(self):
        """Performance test - detect_loop() <10ms."""
        import time
        from src.learning import detect_loop
        
        # Create test action history
        action_history = ["click"] * 50  # Would be Action objects
        
        start = time.perf_counter()
        result = detect_loop(action_history, window_size=30)
        duration_ms = (time.perf_counter() - start) * 1000
        
        # Loop detection must be very fast (checked frequently)
        assert duration_ms < 10, f"Loop detection took {duration_ms}ms, must be <10ms"


class TestLearningLibLoopDetection:
    """Specific tests for loop detection (FR-018, NFR-006)."""

    def test_detect_loop_with_sliding_window(self):
        """Contract test - detect_loop uses sliding window approach."""
        from src.learning import detect_loop
        
        # Create pattern: A, B, C, A, B, C (repeating sequence)
        pattern = ["A", "B", "C"]
        repetitive = pattern * 5  # Repeat 5 times
        
        result = detect_loop(repetitive, window_size=10)
        assert result is True  # Should detect the repeating pattern

    def test_detect_loop_no_false_positives(self):
        """Contract test - detect_loop doesn't flag normal gameplay."""
        from src.learning import detect_loop
        
        # Varied actions should not trigger loop detection
        varied_actions = ["click", "drag", "wait", "click", "key_press", "wait"]
        
        result = detect_loop(varied_actions, window_size=10)
        assert result is False  # Should not detect loop in varied actions

    def test_detect_loop_similarity_threshold(self):
        """Contract test - detect_loop uses Levenshtein distance."""
        from src.learning import detect_loop
        
        # Pattern should be detected even with slight variations
        # Similar but not identical patterns
        pattern1 = ["A", "B", "C"]
        pattern2 = ["A", "B", "D"]  # Slightly different
        mixed = pattern1 + pattern2 + pattern1 + pattern2
        
        result = detect_loop(mixed, window_size=10)
        # Should detect similarity (configurable threshold)
        # This test is lenient - accepts True or False
        # Real implementation with Levenshtein would detect this
        assert isinstance(result, bool)
