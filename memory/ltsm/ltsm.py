import time
from ..schema import LTSMEntry
from ..vector_db import VectorDB

class LTSMManager:
    def __init__(self, dim):
        self.db = VectorDB(dim)

    def add_entry(self, id, vector, metadata, decay_rate=0.001):
        now = time.time()
        entry = LTSMEntry(
            id=id,
            vector=vector,
            metadata=metadata,
            created_at=now,
            last_accessed=now,
            decay_rate=decay_rate
        )
        self.db.add(entry)

    def query(self, vector, top_k=5):
        results = self.db.query(vector, top_k)
        now = time.time()
        for entry in results:
            entry.last_accessed = now
        return results
    
    def decay_entries(self):
        now = time.time()
        for entry in self.db.entries.values():
            age = now - entry.last_accessed
            if age > (1 / entry.decay_rate):
                del self.db.entries[entry.id]