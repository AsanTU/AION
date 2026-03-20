import unittest

from memory.managers.episodic import EpisodicMemory
from memory.storage.sqlite_storage import load_memories, delete_memory

class TestEpisodicMemory(unittest.TestCase):

    def setUp(self):
        for entry in load_memories():
            if getattr(entry, "type", None) == "episodic":
                delete_memory(entry.id)

    def test_add_and_retrieve(self):
        em = EpisodicMemory()
        em.add_entry(
            situation="Test situation",
            decision="Test decision",
            outcome="Test outcome",
            confidence=0.8,
            tags=["test", "success"]
        )
        all_entries = em.get_all()
        self.assertEqual(len(all_entries), 1)
        self.assertEqual(all_entries[0].metadata["decision"], "Test decision")    
        
    def test_find_by_tag(self):
        em = EpisodicMemory()
        em.add_entry("S1", "D1", "O1", 0.7, tags=["failure"])
        em.add_entry("S2", "D2", "O2", 0.9, tags=["success"])
        failure = em.find_by_tag("failure")
        self.assertEqual(len(failure), 1)
        self.assertEqual(failure[0].tags, ["failure"])

    def test_add_entries_batch(self):
        em = EpisodicMemory()
        data = [
            {"situation": "S1", "decision": "D1", "outcome": "O1", "confidence": 0.5, "tags": ["a"]},
            {"situation": "S2", "decision": "D2", "outcome": "O2", "confidence": 0.7, "tags": ["b"]}
        ]
        entries = em.add_entries_batch(data)
        self.assertEqual(len(entries), 2)
        all_entries = em.get_all()
        self.assertTrue(any(e.metadata["decision"] == "D1" for e in all_entries))
        self.assertTrue(any(e.metadata["decision"] == "D2" for e in all_entries))

    def test_delete_entry(self):
        em = EpisodicMemory()
        entry = em.add_entry("S", "D", "O", 0.5)
        em.delete_entry(entry.id)
        self.assertFalse(any(e.id == entry.id for e in em.get_all()))

    def test_importance_and_confidence(self):
        em = EpisodicMemory()
        entry = em.add_entry("S", "D", "O", 0.9, signals={"emotion": 1.0})
        self.assertGreater(entry.importance, 0)
        self.assertEqual(entry.confidence, 0.9)

if __name__ == "__main__":
    unittest.main()