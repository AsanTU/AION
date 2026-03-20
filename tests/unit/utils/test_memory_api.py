import unittest
from memory.api import MemoryAPI
from memory.core.schema import MemoryEntry
import time

class DummyLTSM:
    def read(self, query, top_k=5, tag_filter=None):
        now = int(time.time())
        return [
            MemoryEntry(
                id="1",
                content="A",
                importance=0.9,
                decay_rate=0.01,
                last_accessed=now,
                created_at=now,
                tags=["decision"],
                embedding=[0.1] * 8
            ),
            MemoryEntry(
                id="2",
                content="B",
                importance=0.5,
                decay_rate=0.02,
                last_accessed=now,
                created_at=now,
                tags=["decision"],
                embedding=[0.2] * 8
            )
        ]
    
class TestMemoryAPI(unittest.TestCase):
    def test_query_returns_noramlized_confidence(self):
        api = MemoryAPI(DummyLTSM())
        results = api.query(query="test", tags=["decision"], time_window="12 months")
        self.assertEqual(len(results), 2)
        self.assertTrue(all(0.0 <= r["confidence_score"] <= 1.0 for r in results))
        self.assertIn("why_selected", results[0])
        self.assertIn("content", results[0])

if __name__ == "__main__":
    unittest.main()