import unittest
from unittest.mock import patch
from memory.managers.ltsm import LTSMManager
from memory.core.schema import MemoryEntry

class TestLTSMManager(unittest.TestCase):
    def setUp(self):
        self.ltsm = LTSMManager(dim=3)

    def test_add_entries_batch(self):
        entries_data = [
            {"id": "b1", "content": "batch1", "embedding": [0.1,0.2,0.3], "importance": 0.5, "decay_rate": 0.0},
            {"id": "b2", "content": "batch2", "embedding": [0.4,0.5,0.6], "importance": 0.7, "decay_rate": 0.0}
        ]
        self.ltsm.add_entries_batch(entries_data)
        self.assertIn("b1", self.ltsm.entries)
        self.assertIn("b2", self.ltsm.entries)

    @patch("memory.api.write_memory", return_value="mock_id")
    def test_write(self, mock_write_memory):
        result = self.ltsm.write(event="event", id="w1", signals={"emotion": 1, "outcome": 1, "reuse": 1})
        self.assertEqual(result, "mock_id")
        mock_write_memory.assert_called_once()

    @patch("memory.api.read_memory", return_value=["mock_result"])
    def test_read(self, mock_read_memory):
        result = self.ltsm.read("query", top_k=1)
        self.assertEqual(result, ["mock_result"])
        mock_read_memory.assert_called_once()

    def test_delete_entry(self):
        entry = MemoryEntry(id="del1", content="delete", embedding=[0.1,0.2,0.3], importance=1.0, decay_rate=0.0)
        self.ltsm.entries[entry.id] = entry
        self.ltsm.delete_entry("del1")
        self.assertNotIn("del1", self.ltsm.entries)

    def test_find_by_tag(self):
        entry = MemoryEntry(id="t1", content="tagged", embedding=[0.1,0.2,0.3], importance=1.0, decay_rate=0.0, tags=["foo"])
        self.ltsm.entries[entry.id] = entry
        results = self.ltsm.find_by_tag("foo")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "t1")

    def test_find_by_type(self):
        entry = MemoryEntry(id="type1", content="typed", embedding=[0.1,0.2,0.3], importance=1.0, decay_rate=0.0, type="bar")
        self.ltsm.entries[entry.id] = entry
        results = self.ltsm.find_by_type("bar")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "type1")

    def test_get_recent(self):
        import time
        entry1 = MemoryEntry(id="r1", content="recent1", embedding=[0.1,0.2,0.3], importance=1.0, decay_rate=0.0)
        entry2 = MemoryEntry(id="r2", content="recent2", embedding=[0.4,0.5,0.6], importance=1.0, decay_rate=0.0)
        entry1.last_accessed = time.time() - 10
        entry2.last_accessed = time.time()
        self.ltsm.entries[entry1.id] = entry1
        self.ltsm.entries[entry2.id] = entry2
        results = self.ltsm.get_recent(n=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "r2")

if __name__ == "__main__":
    unittest.main()