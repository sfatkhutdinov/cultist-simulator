"""
Unit Test: GameState Serialization

T123: Test GameState entity serialization to/from JSON.
"""

import pytest
from datetime import datetime
from src.lib.types import GameState, GameElement, ElementType, Rect, Point


class TestGameStateSerialization:
    """Test GameState serialization and deserialization."""
    
    @pytest.fixture
    def sample_gamestate(self):
        """Create a sample GameState for testing."""
        return GameState(
            timestamp=datetime(2025, 10, 4, 12, 0, 0),
            window_bounds=Rect(x=0, y=0, width=1920, height=1080),
            elements=[
                GameElement(
                    element_type=ElementType.CARD,
                    bounds=Rect(x=100, y=100, width=50, height=70),
                    confidence=0.95
                ),
                GameElement(
                    element_type=ElementType.BUTTON,
                    bounds=Rect(x=200, y=200, width=80, height=30),
                    confidence=0.85
                )
            ],
            text_regions=[],
            metadata={
                "game_phase": "early_game",
                "player_health": 10
            }
        )
    
    def test_gamestate_to_dict(self, sample_gamestate):
        """Test serializing GameState to dictionary."""
        data = sample_gamestate.to_dict()
        
        # Verify structure
        assert isinstance(data, dict)
        assert "timestamp" in data
        assert "elements" in data
        assert "text_regions" in data
        assert "metadata" in data
        
        # Verify timestamp is ISO format
        assert isinstance(data["timestamp"], str)
        assert "2025-10-04" in data["timestamp"]
        
        # Verify elements
        assert len(data["elements"]) == 2
        assert data["elements"][0]["element_type"] == "card"
        assert data["elements"][0]["confidence"] == 0.95
        
        # Verify metadata
        assert data["metadata"]["game_phase"] == "early_game"
    
    def test_gamestate_from_dict(self, sample_gamestate):
        """Test deserializing GameState from dictionary."""
        # Serialize to dict
        data = sample_gamestate.to_dict()
        
        # Deserialize back
        restored = GameState.from_dict(data)
        
        # Verify basic properties
        assert restored.timestamp.year == 2025
        assert restored.timestamp.month == 10
        assert restored.timestamp.day == 4
        
        # Verify elements
        assert len(restored.elements) == 2
        assert restored.elements[0].element_type == ElementType.CARD
        assert restored.elements[0].confidence == 0.95
        
        # Verify metadata
        assert restored.metadata["game_phase"] == "early_game"
        assert restored.metadata["player_health"] == 10
    
    def test_gamestate_roundtrip(self, sample_gamestate):
        """Test that serialization roundtrip preserves data."""
        # Serialize and deserialize
        data = sample_gamestate.to_dict()
        restored = GameState.from_dict(data)
        
        # Should be equivalent
        assert len(sample_gamestate.elements) == len(restored.elements)
        assert sample_gamestate.metadata == restored.metadata
    
    def test_empty_gamestate_serialization(self):
        """Test serializing an empty GameState."""
        empty_state = GameState(
            timestamp=datetime.now(),
            window_bounds=Rect(x=0, y=0, width=1920, height=1080),
            elements=[],
            text_regions=[],
            metadata={}
        )
        
        # Should serialize without errors
        data = empty_state.to_dict()
        assert data["elements"] == []
        assert data["text_regions"] == []
        assert data["metadata"] == {}
        
        # Should deserialize
        restored = GameState.from_dict(data)
        assert len(restored.elements) == 0
        assert len(restored.text_regions) == 0
    
    def test_gamestate_with_complex_metadata(self):
        """Test GameState with nested metadata."""
        state = GameState(
            timestamp=datetime.now(),
            window_bounds=Rect(x=0, y=0, width=1920, height=1080),
            elements=[],
            text_regions=[],
            metadata={
                "resources": {
                    "health": 10,
                    "funds": 100
                },
                "cards": [
                    {"name": "card1", "state": "active"},
                    {"name": "card2", "state": "inactive"}
                ]
            }
        )
        
        # Serialize and deserialize
        data = state.to_dict()
        restored = GameState.from_dict(data)
        
        # Verify nested structures
        assert restored.metadata["resources"]["health"] == 10
        assert len(restored.metadata["cards"]) == 2
        assert restored.metadata["cards"][0]["name"] == "card1"
