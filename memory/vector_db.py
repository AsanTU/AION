import faiss
import numpy as np

from memory.schema import LTSMEntry

class VectorDB:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.entries = {}

    def add(self, entry: LTSMEntry):
        vec = np.array(entry.vector).astype('float32').reshape(1, -1)
        self.index.add(vec)
        self.entries[entry.id] = entry

    def query(self, vector, top_k=5):
        vec = np.array(vector).astype('float32').reshape(1, -1)
        D, I = self.index.search(vec, top_k)
        return [self.entries[list(self.entries.keys())[i]] for i in I[0] if i != -1]