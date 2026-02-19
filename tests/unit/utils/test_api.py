import unittest
from unittest.mock import MagicMock
from memory.api import write_memory

class TestWriteMemoryPipeline(unittest.TestCase):
    def test_write_memory_calls_add_entry_with_embedding_and_metadata(self):
        mock_ltsm = MagicMock()
        event = {
            "text": "User clicked save on document",
            "emotion": 0.7,
            "outcome": 0.9,
            "tags": ["save", "ui"]
        }

        mid = write_memory(event, mock_ltsm, dim=8, signals={"emotion":0.7,"outcome":0.9,"reuse":0.1})

        mock_ltsm.add_entry.assert_called_once()
        call_args = mock_ltsm.add_entry.call_args[0]
        self.assertGreaterEqual(len(call_args), 3)

        call_id = call_args[0]
        embedding = call_args[1]
        metadata = call_args[2]

        self.assertIsInstance(call_id, str)
        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 8)
        self.assertIn("importance", metadata)
        self.assertIn("tags", metadata)
        self.assertIn("content", metadata)

    def test_write_memory_defaults_when_no_signals(self):
        mock_ltsm = MagicMock()
        event = {"text": "Minor UI event"}
        write_memory(event, mock_ltsm, dim=4, signals=None)

        mock_ltsm.add_entry.assert_called_once()
        _, embedding, metadata = mock_ltsm.add_entry.call_args[0][:3]
        self.assertEqual(len(embedding), 4)
        self.assertIn("importance", metadata)
        self.assertEqual(metadata["importance"], 0.5)

if __name__ == "__main__":
    unittest.main()