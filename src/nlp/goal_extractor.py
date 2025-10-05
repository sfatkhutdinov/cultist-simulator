"""
Goal extraction module for narrative text analysis.

This module extracts gameplay objectives from narrative text using:
- Pattern matching for explicit goals
- Keyword analysis for implicit objectives
- Context understanding via embeddings

Performance target: <150ms per extraction
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import re


class GoalType(Enum):
    """Types of gameplay goals."""

    COLLECT = "collect"
    SURVIVE = "survive"
    REACH = "reach"
    AVOID = "avoid"
    UNLOCK = "unlock"
    DISCOVER = "discover"
    PROTECT = "protect"
    UNKNOWN = "unknown"


@dataclass
class Goal:
    """Represents an extracted goal from narrative text."""

    description: str
    goal_type: GoalType
    confidence: float  # 0.0 to 1.0
    keywords: List[str]


class GoalExtractor:
    """
    Extracts gameplay objectives from narrative text.

    Uses pattern matching and keyword analysis to identify:
    - Explicit goals ("You must collect five coins")
    - Implicit objectives ("The door is locked")
    - Survival imperatives ("The shadows approach")
    """

    # Pattern matching rules for explicit goals
    GOAL_PATTERNS = [
        # Explicit imperatives
        (
            r"(?:you must|you need to|you should)\s+(\w+(?:\s+\w+){0,10})",
            GoalType.UNKNOWN,
            0.9,
        ),
        (
            r"(?:collect|gather|obtain|find)\s+(\w+(?:\s+\w+){0,5})",
            GoalType.COLLECT,
            0.8,
        ),
        (
            r"(?:survive|endure|last)\s+(?:until|through|against)?\s*(\w+(?:\s+\w+){0,5})",
            GoalType.SURVIVE,
            0.8,
        ),
        (
            r"(?:reach|get to|travel to|arrive at)\s+(\w+(?:\s+\w+){0,5})",
            GoalType.REACH,
            0.8,
        ),
        (
            r"(?:avoid|escape|flee from|stay away from)\s+(\w+(?:\s+\w+){0,5})",
            GoalType.AVOID,
            0.8,
        ),
        (
            r"(?:unlock|open|unseal)\s+(?:the\s+)?(\w+(?:\s+\w+){0,5})",
            GoalType.UNLOCK,
            0.7,
        ),
        (
            r"(?:discover|learn|uncover|reveal)\s+(\w+(?:\s+\w+){0,5})",
            GoalType.DISCOVER,
            0.7,
        ),
        (
            r"(?:protect|defend|guard|save)\s+(\w+(?:\s+\w+){0,5})",
            GoalType.PROTECT,
            0.8,
        ),
    ]

    # Keywords that suggest implicit goals
    IMPLICIT_KEYWORDS = {
        GoalType.UNLOCK: ["locked", "sealed", "keyhole", "barrier", "blocked"],
        GoalType.COLLECT: ["need", "require", "missing", "insufficient"],
        GoalType.AVOID: ["danger", "threat", "peril", "hazard", "deadly"],
        GoalType.SURVIVE: ["approaching", "coming", "imminent", "dread", "fear"],
        GoalType.DISCOVER: ["mystery", "unknown", "hidden", "secret", "enigma"],
    }

    def extract_goals(self, narrative_text: str) -> List[Goal]:
        """
        Extract goals from narrative text.

        Args:
            narrative_text: Game narrative or description text

        Returns:
            List of identified goals with types and confidence scores

        Performance:
            <150ms per extraction (NFR-002)
        """
        goals = []

        # Handle empty input
        if not narrative_text or not narrative_text.strip():
            return goals

        # Extract explicit goals using patterns
        explicit_goals = self._extract_explicit_goals(narrative_text)
        goals.extend(explicit_goals)

        # Extract implicit goals from keywords
        implicit_goals = self._extract_implicit_goals(narrative_text)
        goals.extend(implicit_goals)

        # Deduplicate similar goals
        goals = self._deduplicate_goals(goals)

        return goals

    def _extract_explicit_goals(self, text: str) -> List[Goal]:
        """Extract goals using pattern matching."""
        goals = []
        text_lower = text.lower()

        for pattern, goal_type, confidence in self.GOAL_PATTERNS:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)

            for match in matches:
                description = match.group(1).strip()

                # Extract keywords from description
                keywords = [w for w in description.split() if len(w) > 2]

                goal = Goal(
                    description=description,
                    goal_type=goal_type,
                    confidence=confidence,
                    keywords=keywords,
                )
                goals.append(goal)

        return goals

    def _extract_implicit_goals(self, text: str) -> List[Goal]:
        """Extract implicit goals from keywords."""
        goals = []
        text_lower = text.lower()

        for goal_type, keywords in self.IMPLICIT_KEYWORDS.items():
            # Check if any keywords are present
            found_keywords = [kw for kw in keywords if kw in text_lower]

            if found_keywords:
                # Create implicit goal
                description = f"implied: {goal_type.value}"

                goal = Goal(
                    description=description,
                    goal_type=goal_type,
                    confidence=0.5,  # Lower confidence for implicit goals
                    keywords=found_keywords,
                )
                goals.append(goal)

        return goals

    def _deduplicate_goals(self, goals: List[Goal]) -> List[Goal]:
        """Remove duplicate or very similar goals."""
        if not goals:
            return goals

        # Simple deduplication by description similarity
        unique_goals = []
        seen_descriptions = set()

        for goal in sorted(goals, key=lambda g: g.confidence, reverse=True):
            # Normalize description for comparison
            normalized = goal.description.lower().strip()

            # Check if we've seen a similar description
            if normalized not in seen_descriptions:
                unique_goals.append(goal)
                seen_descriptions.add(normalized)

        return unique_goals
