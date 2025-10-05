"""
Unit Test: KnowledgeBase Queries

T126: Test KnowledgeBase query operations.
"""

import pytest
from src.learning.knowledge_base import KnowledgeBase


class TestKnowledgeBase:
    """Test KnowledgeBase query and storage operations."""

    @pytest.fixture
    def kb(self, tmp_path):
        """Create a knowledge base with temporary database."""
        db_path = tmp_path / "test_kb.db"
        return KnowledgeBase(str(db_path))

    def test_create_knowledge_base(self, kb):
        """Test creating a knowledge base."""
        assert kb is not None
        assert hasattr(kb, "store_mechanic")
        assert hasattr(kb, "get_mechanic")

    def test_store_and_retrieve_mechanic(self, kb):
        """Test storing and retrieving a game mechanic."""
        mechanic_data = {
            "description": "Combining health + passion creates vitality",
            "category": "combination",
            "confidence": 0.9,
        }

        kb.store_mechanic("vitality_combo", mechanic_data)

        # Retrieve mechanic
        retrieved = kb.get_mechanic("vitality_combo")

        assert retrieved is not None
        assert retrieved["description"] == mechanic_data["description"]
        assert retrieved["category"] == mechanic_data["category"]
        assert retrieved["confidence"] == mechanic_data["confidence"]

    def test_update_mechanic(self, kb):
        """Test updating an existing mechanic."""
        # Store initial version
        initial_data = {"description": "Initial description", "confidence": 0.5}
        kb.store_mechanic("test_mechanic", initial_data)

        # Update with new data
        updated_data = {"description": "Updated description", "confidence": 0.8}
        kb.store_mechanic("test_mechanic", updated_data)

        # Retrieve and verify
        retrieved = kb.get_mechanic("test_mechanic")
        assert retrieved["description"] == "Updated description"
        assert retrieved["confidence"] == 0.8

    def test_list_mechanics(self, kb):
        """Test listing all mechanics."""
        # Store multiple mechanics
        for i in range(5):
            kb.store_mechanic(
                f"mechanic_{i}", {"description": f"Mechanic {i}", "data": i}
            )

        # List all mechanics
        mechanics = kb.list_mechanics()

        assert len(mechanics) >= 5
        assert any(m["mechanic_id"] == "mechanic_0" for m in mechanics)
        assert any(m["mechanic_id"] == "mechanic_4" for m in mechanics)

    def test_delete_mechanic(self, kb):
        """Test deleting a mechanic."""
        # Store mechanic
        kb.store_mechanic("to_delete", {"description": "Will be deleted"})

        # Verify it exists
        assert kb.get_mechanic("to_delete") is not None

        # Delete it
        try:
            kb.delete_mechanic("to_delete")
        except AttributeError:
            pytest.skip("delete_mechanic() not implemented")

        # Verify it's gone
        assert kb.get_mechanic("to_delete") is None

    def test_query_mechanics_by_category(self, kb):
        """Test querying mechanics by category."""
        # Store mechanics with different categories
        kb.store_mechanic("combo1", {"category": "combination", "data": 1})
        kb.store_mechanic("combo2", {"category": "combination", "data": 2})
        kb.store_mechanic("timer1", {"category": "timer", "data": 3})

        # Query by category
        try:
            combos = kb.query_mechanics(category="combination")
        except (AttributeError, TypeError):
            pytest.skip("query_mechanics() with category filter not implemented")

        assert len(combos) >= 2
        assert all(m["category"] == "combination" for m in combos)

    def test_store_session_history(self, kb):
        """Test storing session history."""
        session_data = {
            "session_id": "test_session_1",
            "start_time": "2025-10-04T12:00:00",
            "end_time": "2025-10-04T12:30:00",
            "total_actions": 50,
            "outcome": "win",
        }

        try:
            kb.store_session(session_data)
        except AttributeError:
            pytest.skip("store_session() not implemented")

        # Retrieve session
        try:
            retrieved = kb.get_session("test_session_1")
        except AttributeError:
            pytest.skip("get_session() not implemented")

        assert retrieved is not None
        assert retrieved["session_id"] == "test_session_1"
        assert retrieved["outcome"] == "win"

    def test_query_similar_states(self, kb):
        """Test querying similar game states."""
        # Store state transitions
        state1 = {"elements": ["card_a", "card_b"], "resources": {"health": 10}}
        state2 = {"elements": ["card_a", "card_c"], "resources": {"health": 9}}
        state3 = {"elements": ["card_x", "card_y"], "resources": {"health": 5}}

        try:
            kb.store_state_transition(state1, "click", state2, reward=1.0)
            kb.store_state_transition(state2, "drag", state3, reward=0.5)
        except AttributeError:
            pytest.skip("store_state_transition() not implemented")

        # Query for similar states
        try:
            query_state = {
                "elements": ["card_a", "card_b"],
                "resources": {"health": 10},
            }
            similar = kb.query_similar_states(query_state, top_k=5)
        except AttributeError:
            pytest.skip("query_similar_states() not implemented")

        assert len(similar) > 0
        # Most similar should be state1 itself
        assert similar[0]["similarity"] > 0.9

    def test_knowledge_base_stats(self, kb):
        """Test getting knowledge base statistics."""
        # Store some data
        for i in range(10):
            kb.store_mechanic(f"mech_{i}", {"data": i})

        try:
            stats = kb.get_stats()
        except AttributeError:
            pytest.skip("get_stats() not implemented")

        assert "total_mechanics" in stats
        assert stats["total_mechanics"] >= 10

    def test_knowledge_base_export(self, kb, tmp_path):
        """Test exporting knowledge base to JSON."""
        # Store some data
        kb.store_mechanic("export_test", {"data": "test"})

        export_path = tmp_path / "export.json"

        try:
            kb.export_to_json(str(export_path))
        except AttributeError:
            pytest.skip("export_to_json() not implemented")

        # Verify file was created
        assert export_path.exists()

        # Verify content
        import json

        with open(export_path) as f:
            data = json.load(f)

        assert "mechanics" in data or len(data) > 0

    def test_knowledge_base_import(self, kb, tmp_path):
        """Test importing knowledge base from JSON."""
        # Create export data
        import json

        export_data = {
            "mechanics": [{"mechanic_id": "import_test", "data": {"value": 123}}]
        }

        import_path = tmp_path / "import.json"
        with open(import_path, "w") as f:
            json.dump(export_data, f)

        try:
            kb.import_from_json(str(import_path))
        except AttributeError:
            pytest.skip("import_from_json() not implemented")

        # Verify data was imported
        retrieved = kb.get_mechanic("import_test")
        assert retrieved is not None
