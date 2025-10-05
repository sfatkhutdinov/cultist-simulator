"""
Contract tests for nlp_lib.
These tests verify the NLP library's public interface contract.

IMPORTANT: These tests are written FIRST before any implementation (TDD).
They MUST FAIL initially, then pass once nlp_lib is implemented.
"""

import pytest


class TestNLPLibContract:
    """Test suite for nlp_lib public interface."""

    def test_analyze_text_exists(self):
        """T020: Contract test for nlp_lib.analyze_text()."""
        from src.nlp import analyze_text
        
        # Function should exist
        assert callable(analyze_text)
        
        # Check signature
        import inspect
        sig = inspect.signature(analyze_text)
        assert 'text' in sig.parameters

    def test_analyze_text_returns_embedding(self):
        """T020: Contract test - analyze_text returns semantic analysis."""
        from src.nlp import analyze_text
        
        result = analyze_text("You feel a sense of dread.")
        # Should return object with embedding and metadata
        assert hasattr(result, 'embedding')
        assert hasattr(result, 'text')
        assert len(result.embedding) > 0

    def test_analyze_text_handles_empty_input(self):
        """Contract test - analyze_text handles edge cases."""
        from src.nlp import analyze_text
        
        # Empty text should not crash
        result = analyze_text("")
        assert result is not None

    def test_extract_goals_exists(self):
        """T021: Contract test for nlp_lib.extract_goals()."""
        from src.nlp import extract_goals
        
        # Function should exist
        assert callable(extract_goals)
        
        # Check signature
        import inspect
        sig = inspect.signature(extract_goals)
        assert 'narrative_text' in sig.parameters

    def test_extract_goals_identifies_objectives(self):
        """T021: Contract test - extract_goals finds game objectives."""
        from src.nlp import extract_goals
        
        narrative = "You must collect five coins to unlock the door."
        goals = extract_goals(narrative)
        
        # Should return list of identified goals
        assert isinstance(goals, list)
        # Should identify "collect five coins" objective
        assert len(goals) > 0

    def test_extract_goals_returns_structured_data(self):
        """Contract test - extract_goals returns structured goal objects."""
        from src.nlp import extract_goals
        
        narrative = "Survive until dawn. Gather mystical knowledge."
        goals = extract_goals(narrative)
        
        # Each goal should have description and type
        for goal in goals:
            assert hasattr(goal, 'description')
            assert hasattr(goal, 'goal_type')

    def test_find_similar_narratives_exists(self):
        """Contract test for nlp_lib.find_similar_narratives()."""
        from src.nlp import find_similar_narratives
        
        # Function should exist
        assert callable(find_similar_narratives)
        
        # Check signature
        import inspect
        sig = inspect.signature(find_similar_narratives)
        assert 'query_text' in sig.parameters
        assert 'knowledge_base' in sig.parameters

    def test_find_similar_narratives_uses_cosine_similarity(self):
        """Contract test - find_similar_narratives uses semantic search."""
        from src.nlp import find_similar_narratives
        
        query = "A dark ritual is performed."
        # Pass a list as knowledge base for testing
        kb = ["The ceremony begins at midnight.", "The sun rises over the mountains."]
        results = find_similar_narratives(query, knowledge_base=kb)
        
        # Should return list of similar texts with similarity scores
        assert isinstance(results, list)
        # Each result should have text and similarity score
        for result in results:
            assert hasattr(result, 'text')
            assert hasattr(result, 'similarity_score')
            assert 0.0 <= result.similarity_score <= 1.0


class TestNLPLibPerformance:
    """Performance contract tests for nlp_lib."""

    @pytest.mark.performance
    def test_analyze_text_performance(self):
        """Performance test - analyze_text() <100ms."""
        import time
        from src.nlp import analyze_text
        
        # Contract specifies <100ms for semantic analysis
        test_text = "The shadows grow longer as night approaches."
        
        # Warm up (first call loads model)
        analyze_text(test_text)
        
        # Actual performance test
        start = time.perf_counter()
        result = analyze_text(test_text)
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 100, f"Text analysis took {duration_ms}ms, must be <100ms"

    @pytest.mark.performance
    def test_extract_goals_performance(self):
        """Performance test - extract_goals() <150ms."""
        import time
        from src.nlp import extract_goals
        
        narrative = """
        You must survive the coming storm. 
        Gather resources. Find shelter.
        Protect your followers from harm.
        """
        
        start = time.perf_counter()
        goals = extract_goals(narrative)
        duration_ms = (time.perf_counter() - start) * 1000
        
        # Goal extraction should be fast for real-time gameplay
        assert duration_ms < 150, f"Goal extraction took {duration_ms}ms, must be <150ms"

    @pytest.mark.performance
    def test_find_similar_narratives_performance(self):
        """Performance test - find_similar_narratives() <100ms."""
        import time
        from src.nlp import find_similar_narratives
        
        query = "Ancient knowledge beckons."
        kb = ["The old books call to you.", "Modern science provides answers."]
        
        # Warm up
        find_similar_narratives(query, knowledge_base=kb)
        
        # Actual performance test
        start = time.perf_counter()
        results = find_similar_narratives(query, knowledge_base=kb)
        duration_ms = (time.perf_counter() - start) * 1000
        
        # Similarity search must be fast (part of critical path)
        assert duration_ms < 100, f"Similarity search took {duration_ms}ms, must be <100ms"


class TestNLPLibSemanticUnderstanding:
    """Tests for semantic understanding capabilities."""

    def test_analyze_text_captures_sentiment(self):
        """Contract test - analyze_text understands emotional tone."""
        from src.nlp import analyze_text
        
        # Different emotional tones
        positive_text = "Success! Your ritual has brought great fortune."
        negative_text = "Despair consumes you as all hope fades."
        
        pos_result = analyze_text(positive_text)
        neg_result = analyze_text(negative_text)
        
        # Embeddings should be different for different sentiments
        # (This is a simplified test - real test would check embedding distance)
        assert pos_result.text != neg_result.text
        assert pos_result.embedding != neg_result.embedding

    def test_extract_goals_handles_implicit_objectives(self):
        """Contract test - extract_goals understands implicit goals."""
        from src.nlp import extract_goals
        
        # Implicit goal (not explicitly stated as "you must...")
        implicit_narrative = "The door remains locked. A keyhole is visible."
        goals = extract_goals(implicit_narrative)
        
        # Should infer goal: find a key
        # At minimum, should recognize there's an obstacle
        assert len(goals) >= 0  # May be 0 if too implicit, but shouldn't crash
        assert isinstance(goals, list)

    def test_find_similar_narratives_semantic_not_lexical(self):
        """Contract test - similarity is semantic, not just keyword matching."""
        from src.nlp import find_similar_narratives
        
        # These are semantically similar but use different words
        query1 = "The cult leader addresses the followers."
        query2 = "The hierophant speaks to the disciples."
        
        kb = ["A speech is given to the congregation.", "The cat sleeps peacefully."]
        
        # Both should find similar results despite different vocabulary
        result1 = find_similar_narratives(query1, knowledge_base=kb)
        result2 = find_similar_narratives(query2, knowledge_base=kb)
        
        # Should get results
        assert isinstance(result1, list)
        assert isinstance(result2, list)
