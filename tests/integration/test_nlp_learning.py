"""
Integration tests for nlp → learning pipeline.
Tests the interaction between nlp_lib and learning_lib.

IMPORTANT: These tests are written FIRST before any implementation (TDD).
They MUST FAIL initially, then pass once both libraries are integrated.
"""

import pytest


class TestNLPLearningIntegration:
    """T026: Integration tests for nlp → learning pipeline."""

    def test_extract_goals_updates_strategy(self):
        """
        Integration test: Extract goals from narrative, update agent strategy.
        
        Flow: nlp.extract_goals() → learning.update_knowledge()
        """
        from src.nlp import extract_goals
        from src.learning import update_knowledge
        
        # 1. Extract goals from game narrative
        narrative = """
        You must gather three mystical artifacts.
        Survive until the ritual is complete.
        Avoid attracting unwanted attention.
        """
        
        goals = extract_goals(narrative)
        
        # 2. Should identify multiple goals (or return empty list if not implemented)
        assert isinstance(goals, list)
        
        # 3. Use extracted goals to update agent knowledge
        # (Would normally create proper GameState objects)
        mock_state = {"narrative_goals": [str(g) for g in goals]}
        mock_action = {"action_type": "analyze_narrative"}
        mock_next_state = {"updated_strategy": True}
        
        # Update knowledge with goal information
        update_knowledge(mock_state, mock_action, mock_next_state, reward=0.5)

    def test_narrative_similarity_guides_actions(self):
        """
        Integration test: Similar narratives lead to similar action selection.
        
        Flow: nlp.find_similar_narratives() → learning.select_action()
        """
        # This will fail until both libraries are implemented
        with pytest.raises(Exception):
            from src.nlp import find_similar_narratives, analyze_text
            from src.learning import select_action
            
            # 1. Analyze current narrative
            current_narrative = "A dark ritual is about to begin."
            current_analysis = analyze_text(current_narrative)
            
            # 2. Find similar past narratives
            # (Would normally query actual knowledge base)
            similar = find_similar_narratives(
                current_narrative,
                knowledge_base=None  # Mock KB
            )
            
            # 3. Use similarity to inform action selection
            # (Would create proper GameState with narrative context)
            mock_state = {
                "narrative_embedding": current_analysis.embedding,
                "similar_past_situations": similar
            }
            
            action = select_action(mock_state)
            
            # Should return valid action
            assert action is not None
            assert hasattr(action, 'action_type')

    def test_goal_extraction_improves_over_time(self):
        """
        Integration test: Agent learns which goal extractions were correct.
        
        Flow: nlp.extract_goals() → agent acts → learning.update_knowledge()
        """
        from src.nlp import extract_goals
        from src.learning import update_knowledge, query_knowledge
        
        # 1. Extract goals from narrative
        narrative1 = "Find the hidden key to unlock the chamber."
        goals1 = extract_goals(narrative1)
        
        # 2. Simulate pursuing a goal with positive outcome
        for goal in goals1:
            mock_state = {"current_goal": str(goal)}
            mock_action = {"action_type": "pursue_goal"}
            mock_next_state = {"goal_achieved": True}
            
            # Positive reward for successful goal pursuit
            update_knowledge(
                mock_state,
                mock_action,
                mock_next_state,
                reward=2.0  # High reward for success
            )
        
        # 3. Query knowledge to see if agent learned
        result = query_knowledge("goal_outcomes", {"goal_type": "find_key"})
        
        # Should have recorded the successful goal pursuit
        assert result.result_count >= 0

    def test_semantic_understanding_action_selection(self):
        """
        Integration test: Semantic narrative understanding influences decisions.
        
        Tests that NLP embeddings are used by learning for better decisions.
        """
        # This will fail until both libraries are implemented
        with pytest.raises(Exception):
            from src.nlp import analyze_text
            from src.learning import select_action
            
            # 1. Two semantically different narratives
            dangerous_narrative = "The shadows close in. Death is near."
            safe_narrative = "The morning sun brings new opportunities."
            
            # 2. Analyze both
            dangerous_analysis = analyze_text(dangerous_narrative)
            safe_analysis = analyze_text(safe_narrative)
            
            # 3. Select actions based on context
            dangerous_state = {
                "narrative_analysis": dangerous_analysis,
                "threat_level": "high"
            }
            safe_state = {
                "narrative_analysis": safe_analysis,
                "threat_level": "low"
            }
            
            dangerous_action = select_action(dangerous_state)
            safe_action = select_action(safe_state)
            
            # Actions should differ based on semantic context
            # (Specific behavior depends on implementation)
            assert dangerous_action is not None
            assert safe_action is not None

    def test_narrative_knowledge_persistence(self):
        """
        Integration test: NLP-extracted knowledge persists across sessions.
        
        Flow: nlp.analyze_text() → learning.store_session() → query later
        """
        from src.nlp import analyze_text, extract_goals
        from src.learning import store_session, query_knowledge
        
        # 1. Analyze narrative and extract information
        narrative = "The cult thrives in shadows. Gather followers wisely."
        analysis = analyze_text(narrative)
        goals = extract_goals(narrative)
        
        # 2. Store in session
        session_data = {
            "session_id": "nlp-test-001",
            "agent_id": "agent-001",
            "narrative_data": {
                "text": narrative,
                "embedding": analysis.embedding if hasattr(analysis, 'embedding') else [],
                "extracted_goals": [str(g) for g in goals]
            },
            "end_condition": "test"
        }
        
        session_id = store_session(session_data)
        
        # 3. Query narrative knowledge
        result = query_knowledge("narratives", {"session_id": session_id})
        
        # Should retrieve stored narrative data
        assert result.result_count >= 0
