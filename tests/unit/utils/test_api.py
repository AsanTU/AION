import unittest
from memory.api import (
    MemoryAPI, summarize, classify_tags, _deterministic_embed,
    estimate_importance_from_signals, read_memory
)
from unittest.mock import MagicMock

class DummyLTSM:
    # Implement minimal stubs as needed for MemoryAPI
    pass

class TestMemoryAPIExtra(unittest.TestCase):
    def setUp(self):
        self.ltsm = MagicMock()
        self.api = MemoryAPI(self.ltsm)

    def test_timeline(self):
        self.ltsm.db.entries = {}  # or mock entries
        result = self.api.timeline()
        self.assertIsInstance(result, list)

    def test_influences(self):
        self.api.query = MagicMock(return_value=[{"id": "1"}])
        result = self.api.influences("decision_id")
        self.assertEqual(result, [{"id": "1"}])

    def test_print_reasoning(self):
        self.api.influences = MagicMock(return_value=[{"id": "1"}])
        # Just ensure it runs without error
        self.api.print_reasoning("decision_id")

    def test_get_memory_history(self):
        self.ltsm.db.entries = {"1": MagicMock(metadata={}, content="", created_at=0, last_accessed=0, importance=0, decay_rate=0, tags=[])}
        result = self.api.get_memory_history("1")
        self.assertIn("id", result)

    def test__compute_decay_curve(self):
        entry = MagicMock(created_at=0, importance=1.0, decay_rate=0.01)
        result = self.api._compute_decay_curve(entry)
        self.assertIsInstance(result, list)

    def test_why_chain(self):
        entry = MagicMock(metadata={"influences": []}, content="", created_at=0, last_accessed=0, importance=0, decay_rate=0, tags=[], id="1")
        self.ltsm.db.entries = {"1": entry}
        result = self.api.why_chain("1")
        self.assertIn("id", result)

    def test_delete_memories(self):
        entry = MagicMock(tags=["test"], content="test")
        self.ltsm.db.entries = {"1": entry}
        self.api.ltsm.db.entries = {"1": entry}
        result = self.api.delete_memories(tag="test")
        self.assertIsInstance(result, int)

class TestApiUtilities(unittest.TestCase):
    def test_summarize(self):
        self.assertIsInstance(summarize({"text": "abc"}), str)

    def test_classify_tags(self):
        self.assertIn("decision", classify_tags({"decision": True}))

    def test_deterministic_embed(self):
        vec = _deterministic_embed("test", dim=8)
        self.assertEqual(len(vec), 8)

    def test_estimate_importance_from_signals(self):
        self.assertIsInstance(estimate_importance_from_signals({"emotion": 1, "outcome": 1, "reuse": 1}), float)

    def test_read_memory(self):
        ltsm = MagicMock()
        ltsm.dim = 8  # <-- Add this line
        ltsm.db._prepare_vector.return_value = [[0.0]*8]
        ltsm.db.index.search.return_value = ([[1.0]], [[0]])
        ltsm.db.entries = {0: MagicMock(type=None, tags=[], importance=1, decay_rate=0, last_accessed=0)}
        result = read_memory("query", ltsm)
        self.assertIsInstance(result, list)

if __name__ == "__main__":
    unittest.main()