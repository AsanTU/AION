import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from memory.backends.vector_db import VectorDB
from memory.core.schema import MemoryEntry

class TestVectorDB(unittest.TestCase):
    @patch("memory.backends.vector_db.faiss.IndexFlatL2")
    def test_add_and_query_returns_entry(self, MockIndex):
        index_mock = MagicMock()
        index_mock.search.return_value = (np.array([[0.0]], dtype="float32"), np.array([[0]], dtype="int64"))
        MockIndex.return_value = index_mock

        db = VectorDB(dim=3)
        entry = MemoryEntry(id="e1", content="c", embedding=[0.1, 0.2, 0.3], type="test")
        db.add(entry)

        results = db.query([0.1, 0.2, 0.3], top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "e1")
        index_mock.add.assert_called_once()
        index_mock.search.assert_called_once()

    @patch("memory.backends.vector_db.faiss.IndexFlatL2")
    def test_query_ignores_negative_indices(self, MockIndex):
        index_mock = MagicMock()
        index_mock.search.return_value = (
            np.array([[0.0, 0.0]], dtype="float32"),
            np.array([[0, -1]], dtype="int64"),
        )
        MockIndex.return_value = index_mock

        db = VectorDB(dim=3)
        e1 = MemoryEntry(id="e1", content="c1", embedding=[0.1, 0.2, 0.3], type="t")
        e2 = MemoryEntry(id="e2", content="c2", embedding=[0.4, 0.5, 0.6], type="t")
        db.add(e1)
        db.add(e2)

        results = db.query([0.1, 0.2, 0.3], top_k=2)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "e1")

    @patch("memory.backends.vector_db.faiss.IndexFlatL2")
    def test_add_calls_index_add_with_correct_shape(self, MockIndex):
        index_mock = MagicMock()
        MockIndex.return_value = index_mock

        db = VectorDB(dim=3)
        entry = MemoryEntry(id="e1", content="c", embedding=[1, 2, 3], type="t")
        db.add(entry)

        called_arg = index_mock.add.call_args[0][0]
        np.testing.assert_array_equal(called_arg, np.array(entry.embedding, dtype="float32").reshape(1, -1))

if __name__ == "__main__":
    unittest.main()