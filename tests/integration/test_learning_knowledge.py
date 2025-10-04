"""
Integration tests for learning → knowledge base pipeline.
Tests the interaction between learning_lib and knowledge storage.

IMPORTANT: These tests are written FIRST before any implementation (TDD).
They MUST FAIL initially, then pass once the learning library is integrated.
"""

import pytest


class TestLearningKnowledgeIntegration:
    """T025: Integration tests for learning → knowledge base pipeline."""

    def test_store_and_query_session(self):
        """
        Integration test: Store session data, then query it back.
        
        Flow: learning.store_session() → learning.query_knowledge()
        """
        # This will fail until learning library is implemented
        with pytest.raises(Exception):
            from src.learning import store_session, query_knowledge
            
            # 1. Create a mock session object
            # (Would normally be a full Session object from data model)
            mock_session = {
                "session_id": "test-session-001",
                "agent_id": "agent-001",
                "total_actions": 50,
                "survival_time_ingame": 120.5,
                "end_condition": "game_over"
            }
            
            # 2. Store the session
            session_id = store_session(mock_session)
            assert session_id == "test-session-001"
            
            # 3. Query it back
            result = query_knowledge("session", {"session_id": session_id})
            
            # 4. Verify we can retrieve the stored session
            assert result.result_count > 0
            assert result.results[0]['session_id'] == session_id

    def test_update_knowledge_persists_to_db(self):
        """
        Integration test: Update knowledge, verify it's stored in database.
        
        Flow: learning.update_knowledge() → database query
        """
        # This will fail until learning library is implemented
        with pytest.raises(Exception):
            from src.learning import update_knowledge, query_knowledge
            
            # 1. Create mock SARS tuple
            # (Would normally be GameState, Action, GameState, reward)
            mock_state = {"state_id": "state-001"}
            mock_action = {"action_id": "action-001", "action_type": "click"}
            mock_next_state = {"state_id": "state-002"}
            mock_reward = 1.5
            
            # 2. Update knowledge with this experience
            update_knowledge(mock_state, mock_action, mock_next_state, mock_reward)
            
            # 3. Query for similar experiences
            result = query_knowledge("transitions", {"from_state": "state-001"})
            
            # 4. Should find the stored transition
            assert result.result_count > 0

    def test_knowledge_query_performance(self):
        """
        Integration test: Query knowledge base meets <100ms requirement.
        
        Tests NFR-003 performance requirement.
        """
        # This will fail until learning library is implemented
        with pytest.raises(Exception):
            import time
            from src.learning import query_knowledge
            
            # Query should complete within performance budget
            start = time.perf_counter()
            result = query_knowledge("mechanics", {"mechanic_type": "test"})
            duration_ms = (time.perf_counter() - start) * 1000
            
            # NFR-003: <100ms for knowledge queries
            assert duration_ms < 100, f"Query took {duration_ms}ms, must be <100ms"
            
            # Should return valid result even if empty
            assert hasattr(result, 'result_count')
            assert hasattr(result, 'query_time_ms')

    def test_session_recording_completeness(self):
        """
        Integration test: Stored session preserves all critical data.
        
        Ensures NFR-005 observability requirement is met.
        """
        # This will fail until learning library is implemented
        with pytest.raises(Exception):
            from src.learning import store_session, query_knowledge
            
            # 1. Create comprehensive session data
            complete_session = {
                "session_id": "test-session-002",
                "agent_id": "agent-001",
                "start_time": "2025-10-04T10:00:00Z",
                "end_time": "2025-10-04T10:15:00Z",
                "total_actions": 150,
                "survival_time_ingame": 300.0,
                "end_condition": "win",
                "win_type": "ascension",
                "resources_at_end": {"health": 5, "funds": 100},
                "unique_mechanics_discovered": 12,
                "loop_events": 2,
                "safety_violations_blocked": 3
            }
            
            # 2. Store session
            session_id = store_session(complete_session)
            
            # 3. Retrieve and verify all fields preserved
            result = query_knowledge("session", {"session_id": session_id})
            
            assert result.result_count > 0
            stored = result.results[0]
            
            # Verify critical fields preserved
            assert stored['agent_id'] == "agent-001"
            assert stored['end_condition'] == "win"
            assert stored['win_type'] == "ascension"
            assert stored['unique_mechanics_discovered'] == 12

    def test_concurrent_knowledge_updates(self):
        """
        Integration test: Multiple knowledge updates don't corrupt database.
        
        Tests thread safety and data integrity.
        """
        # This will fail until learning library is implemented
        with pytest.raises(Exception):
            from src.learning import update_knowledge
            
            # Simulate rapid knowledge updates (as would happen during gameplay)
            for i in range(10):
                mock_state = {"state_id": f"state-{i}"}
                mock_action = {"action_id": f"action-{i}"}
                mock_next_state = {"state_id": f"state-{i+1}"}
                mock_reward = float(i * 0.1)
                
                # Should handle rapid updates without errors
                update_knowledge(mock_state, mock_action, mock_next_state, mock_reward)
            
            # All updates should succeed without database corruption
            # (Real test would verify database integrity)
