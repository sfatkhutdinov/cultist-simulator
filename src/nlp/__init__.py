"""
NLP Library - Natural Language Processing for Cultist Simulator AI Agent.

This library provides narrative understanding capabilities:
- Semantic text analysis using sentence-transformers
- Goal extraction from narrative text
- Similarity search for finding related content

Public API:
- analyze_text(text) -> TextAnalysis
- extract_goals(narrative_text) -> List[Goal]
- find_similar_narratives(query_text, knowledge_base) -> List[SimilarityResult]

Performance requirements:
- analyze_text: <100ms (NFR-002)
- extract_goals: <150ms (NFR-002)
- find_similar_narratives: <100ms (NFR-002)

Dependencies:
- sentence-transformers: For semantic embeddings
- numpy: For vector operations
"""

from typing import List, Optional
from dataclasses import dataclass
import time

from .text_analyzer import TextAnalyzer, TextEmbedding
from .goal_extractor import GoalExtractor, Goal, GoalType

# Re-export for public API
__all__ = [
    "analyze_text",
    "extract_goals",
    "find_similar_narratives",
    "TextAnalysis",
    "Goal",
    "GoalType",
    "SimilarityResult",
]

# Global instances for performance (avoid reloading models)
_text_analyzer = None
_goal_extractor = None


def _get_text_analyzer() -> TextAnalyzer:
    """Get or create global TextAnalyzer instance."""
    global _text_analyzer
    if _text_analyzer is None:
        _text_analyzer = TextAnalyzer()
    return _text_analyzer


def _get_goal_extractor() -> GoalExtractor:
    """Get or create global GoalExtractor instance."""
    global _goal_extractor
    if _goal_extractor is None:
        _goal_extractor = GoalExtractor()
    return _goal_extractor


@dataclass
class TextAnalysis:
    """Result of text semantic analysis."""

    text: str
    embedding: list  # Convert numpy array to list for serialization
    model_name: str
    processing_time_ms: float


@dataclass
class SimilarityResult:
    """Result from similarity search."""

    text: str
    similarity_score: float
    metadata: Optional[dict] = None


def analyze_text(text: str) -> TextAnalysis:
    """
    Analyze text and generate semantic embedding.

    This function uses sentence-transformers to create a dense vector
    representation of the text that captures its semantic meaning.

    Args:
        text: Text to analyze

    Returns:
        TextAnalysis with embedding and metadata

    Performance:
        <100ms per text (NFR-002)

    Example:
        >>> result = analyze_text("You feel a sense of dread.")
        >>> len(result.embedding)
        384
        >>> result.processing_time_ms < 100
        True
    """
    start_time = time.perf_counter()

    # Handle empty input
    if not text or not text.strip():
        return TextAnalysis(
            text=text, embedding=[], model_name="none", processing_time_ms=0.0
        )

    # Get analyzer and generate embedding
    analyzer = _get_text_analyzer()
    text_embedding = analyzer.embed_text(text)

    # Convert numpy array to list for JSON serialization
    embedding_list = text_embedding.embedding.tolist()

    processing_time = (time.perf_counter() - start_time) * 1000

    return TextAnalysis(
        text=text,
        embedding=embedding_list,
        model_name=text_embedding.model_name,
        processing_time_ms=processing_time,
    )


def extract_goals(narrative_text: str) -> List[Goal]:
    """
    Extract gameplay objectives from narrative text.

    Uses pattern matching and keyword analysis to identify:
    - Explicit goals ("You must collect five coins")
    - Implicit objectives ("The door is locked")
    - Survival imperatives ("The shadows approach")

    Args:
        narrative_text: Game narrative or description text

    Returns:
        List of identified goals with types and confidence scores

    Performance:
        <150ms per extraction (NFR-002)

    Example:
        >>> goals = extract_goals("You must collect five coins to unlock the door.")
        >>> len(goals) > 0
        True
        >>> any(g.goal_type == GoalType.COLLECT for g in goals)
        True
    """
    extractor = _get_goal_extractor()
    return extractor.extract_goals(narrative_text)


def find_similar_narratives(
    query_text: str,
    knowledge_base: Optional[object] = None,
    top_k: int = 5,
    threshold: float = 0.5,
) -> List[SimilarityResult]:
    """
    Find narratives similar to query using semantic search.

    Uses cosine similarity of embeddings to find semantically related
    content, not just keyword matches.

    Args:
        query_text: Text to search for
        knowledge_base: Knowledge base to search (if None, returns empty list)
        top_k: Maximum number of results to return
        threshold: Minimum similarity score (0.0 to 1.0)

    Returns:
        List of similar narratives with similarity scores

    Performance:
        <100ms for typical searches (NFR-002)

    Example:
        >>> results = find_similar_narratives(
        ...     "A dark ritual is performed.",
        ...     knowledge_base=my_kb,
        ...     top_k=3
        ... )
        >>> all(0.0 <= r.similarity_score <= 1.0 for r in results)
        True
    """
    start_time = time.perf_counter()

    # Handle no knowledge base case
    if knowledge_base is None:
        return []

    # Get analyzer
    analyzer = _get_text_analyzer()

    # If knowledge_base is a list of strings, search directly
    if isinstance(knowledge_base, list):
        candidates = knowledge_base
    # If knowledge_base has a query method, use it
    elif hasattr(knowledge_base, "get_all_narratives"):
        candidates = knowledge_base.get_all_narratives()
    else:
        # Unsupported knowledge base type
        return []

    # Find similar texts
    similar_texts = analyzer.find_similar_texts(
        query=query_text, candidates=candidates, top_k=top_k, threshold=threshold
    )

    # Convert to SimilarityResult objects
    results = [
        SimilarityResult(
            text=text,
            similarity_score=score,
            metadata={"processing_time_ms": (time.perf_counter() - start_time) * 1000},
        )
        for text, score in similar_texts
    ]

    return results
