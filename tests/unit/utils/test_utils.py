import unittest
import io
import sys
from memory.core.schema import MemoryEntry

import memory.utils.reader as reader
import memory.utils.writer as writer
import memory.utils.decay as decay
import memory.utils.cli as cli

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.entries = [
            MemoryEntry(
                id="1", content="a", embedding=[], type="foo", tags=["x", "y"], importance=1.0,
                confidence=0.5, created_at=1, last_accessed=10, decay_rate=0.01, source="src", linked_memories=[], metadata={}
            ),
            MemoryEntry(
                id="2", content="b", embedding=[], type="bar", tags=["y"], importance=0.5,
                confidence=0.5, created_at=2, last_accessed=20, decay_rate=0.01, source="src", linked_memories=[], metadata={}
            ),
        ]

    # --- reader.py ---
    def test_get_memories_by_tag(self):
        result = reader.get_memories_by_tag(self.entries, "x")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "1")

    def test_get_memories_by_type(self):
        result = reader.get_memories_by_type(self.entries, "bar")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "2")

    def test_get_recent_memories(self):
        result = reader.get_recent_memories(self.entries, n=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "2")

    # --- writer.py ---
    def test_save_and_batch_save_memory(self):
        # These just call add_memory, so we check for no exceptions
        writer.save_memory(self.entries[0])
        writer.batch_save_memories(self.entries)

    def test_update_memory(self):
        entry = self.entries[0]
        writer.update_memory(entry, content="updated")
        self.assertEqual(entry.content, "updated")

    # --- decay.py ---
    def test_decay_score(self):
        score = decay.decay_score(importance=1.0, age_days=30, decay_factor=30)
        self.assertAlmostEqual(score, 1.0 * (2.718281828459045 ** -1), places=5)

    # --- cli.py ---
    def test_print_reasoning_memories(self):
        # Capture stdout
        captured = io.StringIO()
        sys.stdout = captured
        cli.print_reasoning_memories(self.entries, decision="Test decision")
        sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn("Decision: Test decision", output)
        self.assertIn("1. a", output)
        self.assertIn("2. b", output)

if __name__ == "__main__":
    unittest.main()