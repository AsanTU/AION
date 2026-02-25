import unittest
from memory.api import MemoryAPI
from memory.core.schema import MemoryEntry

class DummyLTSM:
    def read(self, query, top_k=5, tag_filter=None):
        return [
            MemoryEntry(id="1",content="A", importance=0.9, decay_rate=0.01, last_accessed=1000, created_at=1000, tags=["decision"]),
            MemoryEntry(id="2",content="B", importance=0.5, decay_rate=0.02, last_accessed=1000, created_at=1000, tags=["decision"]),
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