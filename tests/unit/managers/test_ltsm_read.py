import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from memory.managers.ltsm import LTSMManager
from memory.core.schema import MemoryEntry

class TestLTSMReadPipeline(unittest.TestCase):
    @patch("memory.backends.vector_db.faiss.IndexFlatL2")
    @patch("memory.backends.vector_db.faiss.IndexIDMap")
    def test_read_returns_top_k_ordered_by_final_score(self, MockIndexIDMap, MockIndexFlat):
        index_mock = MagicMock()
        D = np.array([[0.1, 0.9]], dtype="float32")
        I = np.array([[1, 2]], dtype="int64")
        index_mock.search.return_value = (D, I)
        index_mock.add_with_ids = MagicMock()
        index_mock.remove_ids = MagicMock()
        MockIndexIDMap.return_value = index_mock
        MockIndexFlat.return_value = MagicMock()  

        ltsm = LTSMManager(dim=3)

        e1 = MemoryEntry(id="e1", content="a", embedding=[0.1,0.2,0.3], importance=1.0, decay_rate=0.0)
        e1.metadata["importance"] = 1.0
        ltsm.db.add(e1)

        e2 = MemoryEntry(id="e2", content="b", embedding=[0.4,0.5,0.6], importance=0.5, decay_rate=0.0)
        e2.metadata["importance"] = 0.5
        ltsm.db.add(e2)

        results = ltsm.read("some query", top_k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].id, "e1")
        self.assertEqual(results[1].id, "e2")

        index_mock.search.assert_called_once()

if __name__ == "__main__":
    unittest.main()