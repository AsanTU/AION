import unittest
from memory.managers.ltsm import LTSMManager

class TestLTSMManager(unittest.TestCase):
    def text_add_and_query(self):
        manager = LTSMManager(dim=3)
        manager.add_entry("1", [0.1, 0.2, 0.3], {"type": "fact"}, decay_rate=0.001)
        results = manager.query([0.1, 0.2, 0.3])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "1")

    def test_decay(self):
        manager = LTSMManager(dim=3)
        manager.add_entry("2", [0.4, 0.5, 0.6], {"type": "rule"}, decay_rate=0.00001)
        manager.decay_entries()
        self.assertIn("2", manager.db.entries)

if __name__ == "__main__":
    unittest.main()