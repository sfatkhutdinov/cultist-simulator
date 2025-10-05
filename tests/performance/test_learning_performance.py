"""
Performance Test: Knowledge Base Query Performance

T035: Verify that knowledge base queries complete in <100ms
to meet NFR-003 performance requirement.
"""

import pytest
import time
from src.learning.knowledge_base import KnowledgeBase


class TestLearningPerformance:
    """Performance tests for learning library components."""

    @pytest.fixture
    def kb(self, tmp_path):
        """Create a knowledge base with test database."""
        db_path = tmp_path / "test_kb.db"
        return KnowledgeBase(str(db_path))

    def test_query_knowledge_under_100ms(self, kb):
        """
        Test that knowledge base queries complete in <100ms.

        NFR-003: query_knowledge() must complete in <100ms

        SUCCESS CRITERIA:
        - Query execution time < 100ms
        - Measured over multiple iterations
        - Average time well under threshold
        """
        # Populate some test data
        for i in range(10):
            kb.store_mechanic(
                f"mechanic_{i}",
                {
                    "description": f"Test mechanic {i}",
                    "category": "test",
                    "data": {"value": i},
                },
            )

        # Warm up (first query might be slower due to DB initialization)
        kb.get_mechanic("mechanic_0")

        # Measure query performance
        query_times = []
        iterations = 20

        for i in range(iterations):
            start_time = time.perf_counter()

            # Query by key
            result = kb.get_mechanic(f"mechanic_{i % 10}")

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            query_times.append(elapsed_ms)

            # Verify result is valid
            assert result is not None or i >= 10, "Query should return result"

        # Calculate statistics
        avg_time = sum(query_times) / len(query_times)
        max_time = max(query_times)
        min_time = min(query_times)

        print(f"\nQuery Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        print(f"  Threshold: 100ms")

        # Assert NFR-003 compliance
        assert (
            avg_time < 100
        ), f"Average query time {avg_time:.2f}ms exceeds 100ms threshold"

        # Most queries should be well under threshold
        fast_queries = sum(1 for t in query_times if t < 50)
        assert (
            fast_queries / len(query_times) > 0.8
        ), "At least 80% of queries should complete in <50ms"

    def test_list_mechanics_performance(self, kb):
        """Test that listing mechanics is performant."""
        # Add multiple mechanics
        for i in range(50):
            kb.store_mechanic(f"mechanic_{i}", {"data": i})

        # Measure list performance
        start_time = time.perf_counter()
        mechanics = kb.list_mechanics()
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        print(f"\nList Mechanics Performance:")
        print(f"  Time: {elapsed_ms:.2f}ms")
        print(f"  Count: {len(mechanics)}")

        # Should complete quickly even with 50 items
        assert (
            elapsed_ms < 100
        ), f"List mechanics {elapsed_ms:.2f}ms exceeds 100ms threshold"

        # Verify correct count
        assert len(mechanics) == 50

    def test_store_mechanic_performance(self, kb):
        """Test that storing mechanics is performant."""
        store_times = []

        for i in range(20):
            start_time = time.perf_counter()

            kb.store_mechanic(
                f"perf_mechanic_{i}",
                {
                    "description": f"Performance test mechanic {i}",
                    "complexity": "medium",
                    "effects": ["effect1", "effect2"],
                    "requirements": ["req1", "req2"],
                },
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            store_times.append(elapsed_ms)

        avg_store_time = sum(store_times) / len(store_times)

        print(f"\nStore Mechanic Performance:")
        print(f"  Average: {avg_store_time:.2f}ms")

        # Store operations should also be fast
        assert (
            avg_store_time < 100
        ), f"Average store time {avg_store_time:.2f}ms exceeds 100ms"

    def test_knowledge_base_scalability(self, kb):
        """
        Test performance with larger dataset.

        Ensures KB remains performant as data grows.
        """
        # Add 100 mechanics
        print("\nPopulating KB with 100 mechanics...")
        for i in range(100):
            kb.store_mechanic(
                f"mechanic_{i}",
                {"id": i, "name": f"Mechanic {i}", "type": f"type_{i % 5}"},  # 5 types
            )

        # Query performance with larger dataset
        query_times = []
        for i in range(20):
            start_time = time.perf_counter()
            kb.get_mechanic(f"mechanic_{i * 5}")  # Query every 5th
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            query_times.append(elapsed_ms)

        avg_time = sum(query_times) / len(query_times)

        print(f"Query Performance with 100 mechanics:")
        print(f"  Average: {avg_time:.2f}ms")

        # Should still meet performance requirements
        assert (
            avg_time < 100
        ), f"Query time {avg_time:.2f}ms with 100 mechanics exceeds threshold"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
