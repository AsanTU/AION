import numpy as np
from typing import List, Dict, Optional
from memory.core.schema import MemoryEntry

try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    faiss = None
    _FAISS_AVAILABLE = False

class _InMemoryIndex:
    """Fallback in-memory vector index for environments without FAISS."""
    def __init__(self, dim: int):
        self.dim = dim
        self._vecs: List[np.ndarray] = []
        self._ids: List[int] = []

    def add_with_ids(self, vec: np.ndarray, ids: np.ndarray) -> None:
        for i in range(vec.shape[0]):
            self._vecs.append(vec[i].astype("float32").copy())
            self._ids.append(int(ids[i]))

    def add(self, vec: np.ndarray) -> None:
        start = len(self._vecs)
        for i in range(vec.shape[0]):
            self._vecs.append(vec[i].astype("float32").copy())
            self._ids.append(start + i)

    def remove_ids(self, ids: np.ndarray) -> None:
        remove_set = set(int(x) for x in ids)
        keep = [(v, i) for v, i in zip(self._vecs, self._ids) if i not in remove_set]
        self._vecs = [v for v, _ in keep]
        self._ids = [i for _, i in keep]

    def search(self, qvec: np.ndarray, top_k: int):
        if not self._vecs:
            D = np.full((1, top_k), np.inf, dtype="float32")
            I = np.full((1, top_k), -1, dtype="int64")
            return D, I
        qs = qvec.astype("float32").reshape(-1)
        mat = np.vstack(self._vecs)
        dists = np.sum((mat - qs) ** 2, axis=1)
        order = np.argsort(dists)[:top_k]
        D = np.full((1, top_k), np.inf, dtype="float32")
        I = np.full((1, top_k), -1, dtype="int64")
        for j, idx in enumerate(order):
            D[0, j] = float(dists[idx])
            I[0, j] = int(self._ids[idx])
        return D, I

class VectorDB:
    """
    Vector database using FAISS if available, otherwise a fallback in-memory index.
    Stores MemoryEntry objects and supports similarity search.
    """
    def __init__(self, dim: int):
        self.dim = dim
        self.entries: Dict[str, MemoryEntry] = {}
        self._key_to_id: Dict[str, int] = {}
        self._id_to_key: Dict[int, str] = {}
        self._next_id = 1

        if _FAISS_AVAILABLE:
            base = faiss.IndexFlatL2(dim)
            try:
                self.index = faiss.IndexIDMap(base)
            except Exception:
                self.index = base
        else:
            self.index = _InMemoryIndex(dim)

    def _prepare_vector(self, vec) -> np.ndarray:
        arr = np.asarray(vec)
        if arr.ndim == 2 and arr.shape[0] == 1:
            arr = arr.reshape(-1)
        if arr.ndim != 1:
            raise ValueError(f"embedding must be 1-D (got shape={arr.shape})")
        if arr.shape[0] != self.dim:
            raise ValueError(f"embedding dimension mismatch: expected {self.dim}, got {arr.shape[0]}")
        return arr.astype("float32").reshape(1, -1)

    def _alloc_id(self, key: str) -> int:
        if key in self._key_to_id:
            return self._key_to_id[key]
        fid = self._next_id
        self._next_id += 1
        self._key_to_id[key] = fid
        self._id_to_key[fid] = key
        return fid

    def add(self, entry: MemoryEntry) -> None:
        """
        Add a MemoryEntry to the vector database.
        """
        vec = self._prepare_vector(entry.embedding)
        fid = self._alloc_id(entry.id)
        try:
            if hasattr(self.index, "remove_ids"):
                self.index.remove_ids(np.array([fid], dtype=np.int64))
        except Exception:
            pass
        try:
            ids = np.array([fid], dtype=np.int64)
            if hasattr(self.index, "add_with_ids"):
                self.index.add_with_ids(vec, ids)
            else:
                self.index.add(vec)
        except Exception:
            self.index.add(vec)
        self.entries[entry.id] = entry

    def add_batch(self, entries: List[MemoryEntry]) -> None:
        """
        Add multiple MemoryEntry objects in a batch.
        """
        for entry in entries:
            self.add(entry)

    def query(self, vector, top_k: int = 5) -> List[MemoryEntry]:
        """
        Query the vector database for the top_k most similar MemoryEntry objects.
        """
        vec = self._prepare_vector(vector)
        D, I = self.index.search(vec, top_k)
        results: List[MemoryEntry] = []
        for fid in I[0]:
            if int(fid) == -1:
                continue
            key = self._id_to_key.get(int(fid))
            if key is None:
                continue
            entry = self.entries.get(key)
            if entry is None:
                continue
            results.append(entry)
        return results