import faiss
import numpy as np

from memory.core.schema import MemoryEntry

class VectorDB:
    def __init__(self, dim):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.entries = {}

    def _prepare_vector(self, vec):
        arr = np.asarray(vec)
        if arr.ndim == 2 and arr.shape[0] == 1:
            arr = arr.reshape(-1)
        if arr.ndim != 1:
            raise ValueError(f"embedding must be 1-D (got shape={arr.shape})")
        if arr.shape[0] != self.dim:
            raise ValueError(f"embedding dimesion mismatch: expected {self.dim}, got {arr.shape[0]}")
        return arr.astype("float32").reshape(1, -1)

    def add(self, entry: MemoryEntry):
        vec = self._prepare_vector(entry.embedding)
        self.index.add(vec)
        self.entries[entry.id] = entry

    def query(self, vector, top_k=5):
        vec = self._prepare_vector(vector)
        D, I = self.index.search(vec, top_k)
        keys = list(self.entries.keys())
        return [self.entries[keys[i]] for i in I[0] if i != -1]