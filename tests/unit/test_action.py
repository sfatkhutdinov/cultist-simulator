"""
Unit Test: Action Validation Logic

T124: Test Action entity validation.
"""

import pytest
from datetime import datetime
from src.lib.types import Action, ActionType, Point


class TestActionValidation:
    """Test Action entity validation and behavior."""
    
    def test_create_click_action(self):
        """Test creating a click action."""
        action = Action(
            action_type=ActionType.CLICK,
            parameters={"x": 100, "y": 200, "button": "left"}
        )
        
        assert action.action_type == ActionType.CLICK
        assert action.parameters["x"] == 100
        assert action.parameters["y"] == 200
        assert action.parameters["button"] == "left"
        assert isinstance(action.timestamp, datetime)
    
    def test_create_drag_action(self):
        """Test creating a drag action."""
        action = Action(
            action_type=ActionType.DRAG,
            parameters={
                "start_x": 100,
                "start_y": 200,
                "end_x": 300,
                "end_y": 400,
                "duration": 0.5
            }
        )
        
        assert action.action_type == ActionType.DRAG
        assert action.parameters["start_x"] == 100
        assert action.parameters["end_x"] == 300
        assert action.parameters["duration"] == 0.5
    
    def test_create_key_press_action(self):
        """Test creating a key press action."""
        action = Action(
            action_type=ActionType.KEY_PRESS,
            parameters={"key": "space", "modifiers": []}
        )
        
        assert action.action_type == ActionType.KEY_PRESS
        assert action.parameters["key"] == "space"
        assert action.parameters["modifiers"] == []
    
    def test_create_wait_action(self):
        """Test creating a wait action."""
        action = Action(
            action_type=ActionType.WAIT,
            parameters={"duration": 1.5}
        )
        
        assert action.action_type == ActionType.WAIT
        assert action.parameters["duration"] == 1.5
    
    def test_create_composite_action(self):
        """Test creating a composite action."""
        sub_action1 = Action(
            action_type=ActionType.CLICK,
            parameters={"x": 100, "y": 200, "button": "left"}
        )
        sub_action2 = Action(
            action_type=ActionType.WAIT,
            parameters={"duration": 0.5}
        )
        
        composite = Action(
            action_type=ActionType.COMPOSITE,
            parameters={"sub_actions": [sub_action1, sub_action2]}
        )
        
        assert composite.action_type == ActionType.COMPOSITE
        assert len(composite.parameters["sub_actions"]) == 2
    
    def test_action_with_metadata(self):
        """Test action with metadata."""
        action = Action(
            action_type=ActionType.CLICK,
            parameters={"x": 100, "y": 200},
            metadata={
                "reason": "clicking card",
                "expected_outcome": "card selection",
                "confidence": 0.8
            }
        )
        
        assert action.metadata["reason"] == "clicking card"
        assert action.metadata["confidence"] == 0.8
    
    def test_action_string_representation(self):
        """Test action __str__ method."""
        action = Action(
            action_type=ActionType.CLICK,
            parameters={"x": 100, "y": 200, "button": "left"}
        )
        
        str_repr = str(action)
        assert "click" in str_repr.lower()
        assert "x=100" in str_repr or "100" in str_repr
    
    def test_action_timestamp_default(self):
        """Test that action timestamp is set automatically."""
        before = datetime.now()
        action = Action(
            action_type=ActionType.CLICK,
            parameters={"x": 100, "y": 200}
        )
        after = datetime.now()
        
        assert before <= action.timestamp <= after
    
    def test_action_timestamp_custom(self):
        """Test setting custom timestamp."""
        custom_time = datetime(2025, 10, 4, 12, 0, 0)
        action = Action(
            action_type=ActionType.CLICK,
            parameters={"x": 100, "y": 200},
            timestamp=custom_time
        )
        
        assert action.timestamp == custom_time
    
    def test_validate_click_parameters(self):
        """Test that click actions have required parameters."""
        # Valid click action
        action = Action(
            action_type=ActionType.CLICK,
            parameters={"x": 100, "y": 200}
        )
        
        assert "x" in action.parameters
        assert "y" in action.parameters
        assert isinstance(action.parameters["x"], int)
        assert isinstance(action.parameters["y"], int)
    
    def test_validate_drag_parameters(self):
        """Test that drag actions have required parameters."""
        action = Action(
            action_type=ActionType.DRAG,
            parameters={
                "start_x": 100,
                "start_y": 200,
                "end_x": 300,
                "end_y": 400
            }
        )
        
        assert "start_x" in action.parameters
        assert "start_y" in action.parameters
        assert "end_x" in action.parameters
        assert "end_y" in action.parameters
    
    def test_action_equality(self):
        """Test comparing actions."""
        action1 = Action(
            action_type=ActionType.CLICK,
            parameters={"x": 100, "y": 200},
            timestamp=datetime(2025, 10, 4, 12, 0, 0)
        )
        action2 = Action(
            action_type=ActionType.CLICK,
            parameters={"x": 100, "y": 200},
            timestamp=datetime(2025, 10, 4, 12, 0, 0)
        )
        
        # Actions with same type and parameters should be equal
        assert action1.action_type == action2.action_type
        assert action1.parameters == action2.parameters
