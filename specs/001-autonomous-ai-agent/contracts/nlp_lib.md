# NLP Library Contract

**Library**: `nlp_lib`  
**Purpose**: Semantic understanding of narrative text for informed decision-making  
**Dependencies**: sentence-transformers, scikit-learn

---

## Public Interface

### Functions

#### `analyze_text(text: str) -> SemanticAnalysis`
Performs semantic analysis on narrative text (FR-022).

**Input**: Raw text string from game  
**Output**: SemanticAnalysis with embeddings, extracted goals, sentiment  
**Performance**: <100ms  
**Errors**: `TextProcessingError`

#### `extract_goals(text: str) -> List[str]`
Identifies objectives/quests from narrative text.

**Input**: Narrative text  
**Output**: List of extracted goal descriptions  
**Performance**: <50ms

#### `find_similar_narratives(text: str, top_k: int = 5) -> List[Tuple[str, float]]`
Finds semantically similar previously-seen text.

**Input**: Text to match, number of results  
**Output**: List of (matched_text, similarity_score)  
**Performance**: <100ms

### CLI Interface

```bash
nlp_lib --analyze-text "You have found ancient knowledge" [--output analysis.json]
nlp_lib --extract-goals "Seek the Mansus" [--output goals.json]
nlp_lib --find-similar "mysterious ritual" --top-k 5
```

---

## Data Contracts

### SemanticAnalysis
```python
{
    "text": str,
    "embedding": list[float],  # 384-dimensional vector
    "extracted_goals": list[str],
    "sentiment": "positive" | "negative" | "neutral",
    "confidence": float,
    "processing_time_ms": float
}
```

---

## Testing Requirements

1. `test_analyze_text_returns_valid_embedding()` - Output structure
2. `test_similar_narratives_finds_matches()` - Similarity search
3. `test_goal_extraction_identifies_objectives()` - Goal extraction (FR-022)
4. `test_performance_within_budget()` - <100ms requirement

---

## Configuration

```python
nlp_config = {
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "embedding_dim": 384,
    "similarity_threshold": 0.7,
    "max_text_length": 500
}
```
