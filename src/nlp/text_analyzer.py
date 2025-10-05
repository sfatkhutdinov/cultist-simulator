"""
Text analysis module using sentence-transformers for semantic understanding.

This module provides:
- Text embedding generation using pre-trained models
- Semantic similarity computation
- Embedding caching for performance

Performance targets:
- Embedding generation: <100ms per text
- Similarity search: <100ms
"""

from typing import List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from functools import lru_cache
import hashlib


@dataclass
class TextEmbedding:
    """Represents a text's semantic embedding."""
    text: str
    embedding: np.ndarray
    model_name: str


class TextAnalyzer:
    """
    Analyzes text using sentence-transformers for semantic understanding.
    
    Uses 'all-MiniLM-L6-v2' model by default:
    - Fast inference (~50ms per sentence)
    - Good quality embeddings (384 dimensions)
    - Small model size (~80MB)
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize text analyzer with sentence-transformer model.
        
        Args:
            model_name: Name of sentence-transformers model to use
        """
        self.model_name = model_name
        self._model = None
        self._embedding_cache = {}
    
    def _load_model(self):
        """Lazy-load the sentence-transformers model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def embed_text(self, text: str) -> TextEmbedding:
        """
        Generate semantic embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            TextEmbedding with text and embedding vector
            
        Performance:
            <100ms per text (NFR-002)
        """
        # Check cache first
        cache_key = self._get_cache_key(text)
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        # Load model if needed
        self._load_model()
        
        # Generate embedding
        embedding_vector = self._model.encode(text, convert_to_numpy=True)
        
        result = TextEmbedding(
            text=text,
            embedding=embedding_vector,
            model_name=self.model_name
        )
        
        # Cache result
        self._embedding_cache[cache_key] = result
        
        return result
    
    def compute_similarity(
        self, 
        text1: str, 
        text2: str
    ) -> float:
        """
        Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
            
        Performance:
            <100ms for similarity computation
        """
        # Get embeddings (may be cached)
        emb1 = self.embed_text(text1)
        emb2 = self.embed_text(text2)
        
        # Compute cosine similarity
        similarity = self._cosine_similarity(emb1.embedding, emb2.embedding)
        
        return float(similarity)
    
    def find_similar_texts(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        """
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
        """
        # Get query embedding
        query_emb = self.embed_text(query)
        
        # Compute similarities
        similarities = []
        for candidate in candidates:
            candidate_emb = self.embed_text(candidate)
            similarity = self._cosine_similarity(
                query_emb.embedding, 
                candidate_emb.embedding
            )
            
            if similarity >= threshold:
                similarities.append((candidate, float(similarity)))
        
        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (-1.0 to 1.0, typically 0.0 to 1.0)
        """
        # Normalize vectors
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)
        
        # Compute dot product
        similarity = np.dot(vec1_norm, vec2_norm)
        
        return similarity
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self._embedding_cache.clear()
