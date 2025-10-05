# Nlp API

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

**Module**: `src.nlp`  
**Generated**: 2025-10-04 22:36:32

---

## Table of Contents

- [Functions](#functions)
- [Classes](#classes)

---

## Functions


### `analyze_text(text: str) -> src.nlp.TextAnalysis`

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

---

### `extract_goals(narrative_text: str) -> List[src.nlp.goal_extractor.Goal]`

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

---

### `find_similar_narratives(query_text: str, knowledge_base: Optional[object] = None, top_k: int = 5, threshold: float = 0.5) -> List[src.nlp.SimilarityResult]`

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

---

## Classes


### `class Goal`

Represents an extracted goal from narrative text.

**Methods:**


#### `__init__(self, description: str, goal_type: src.nlp.goal_extractor.GoalType, confidence: float, keywords: List[str]) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class GoalExtractor`

Extracts gameplay objectives from narrative text.

Uses pattern matching and keyword analysis to identify:
- Explicit goals ("You must collect five coins")
- Implicit objectives ("The door is locked")
- Survival imperatives ("The shadows approach")

**Methods:**


#### `extract_goals(self, narrative_text: str) -> List[src.nlp.goal_extractor.Goal]`

Extract goals from narrative text.

Args:
    narrative_text: Game narrative or description text
    
Returns:
    List of identified goals with types and confidence scores
    
Performance:
    <150ms per extraction (NFR-002)

---

### `class GoalType`

Types of gameplay goals.

---

### `class SimilarityResult`

Result from similarity search.

**Methods:**


#### `__init__(self, text: str, similarity_score: float, metadata: Optional[dict] = None) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class TextAnalysis`

Result of text semantic analysis.

**Methods:**


#### `__init__(self, text: str, embedding: list, model_name: str, processing_time_ms: float) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class TextAnalyzer`

Analyzes text using sentence-transformers for semantic understanding.

Uses 'all-MiniLM-L6-v2' model by default:
- Fast inference (~50ms per sentence)
- Good quality embeddings (384 dimensions)
- Small model size (~80MB)

**Methods:**


#### `__init__(self, model_name: str = 'all-MiniLM-L6-v2')`

Initialize text analyzer with sentence-transformer model.

Args:
    model_name: Name of sentence-transformers model to use


#### `clear_cache(self)`

Clear the embedding cache.


#### `compute_similarity(self, text1: str, text2: str) -> float`

Compute semantic similarity between two texts.

Args:
    text1: First text
    text2: Second text
    
Returns:
    Cosine similarity score (0.0 to 1.0)
    
Performance:
    <100ms for similarity computation


#### `embed_text(self, text: str) -> src.nlp.text_analyzer.TextEmbedding`

Generate semantic embedding for text.

Args:
    text: Text to embed
    
Returns:
    TextEmbedding with text and embedding vector
    
Performance:
    <100ms per text (NFR-002)


#### `find_similar_texts(self, query: str, candidates: List[str], top_k: int = 5, threshold: float = 0.0) -> List[Tuple[str, float]]`

Find most similar texts from candidates.

Args:
    query: Query text
    candidates: List of candidate texts to search
    top_k: Number of top results to return
    threshold: Minimum similarity threshold (0.0 to 1.0)
    
Returns:
    List of (text, similarity_score) tuples, sorted by similarity
    
Performance:
    <100ms for typical searches

---

### `class TextEmbedding`

Represents a text's semantic embedding.

**Methods:**


#### `__init__(self, text: str, embedding: numpy.ndarray, model_name: str) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---
