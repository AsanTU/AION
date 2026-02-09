import unittest

from memory.episodic import EpisodicMemory

class TestEpisodicMemory(unittest.TestCase):
    def test_add_and_retrieve(self):
        em = EpisodicMemory()
        em.add_entry(
            situation="Test situation",
            decisioin="Test decision",
            outcome="Test outcome",
            confidence=0.8,
            tags=["test", "success"]
        )
        all_entries = em.get_all()
        self.assertEqual(len(all_entries), 1)
        self.assertEqual(all_entries[0].decision, "Test decision")
    
    def test_find_by_tag(self):
        em = EpisodicMemory()
        em.add_entry("S1", "D1", "O1", 0.7, tags=["failure"])
        em.add_entry("S2", "D2", "O2", 0.9, tags=["success"])
        failure = em.find_by_tag("failure")
        self.assertEqual(len(failure), 1)
        self.assertEqual(failure[0].tags, ["failure"])

if __name__ == "__main__":
    unittest.main()