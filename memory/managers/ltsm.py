import time
from memory.core.schema import MemoryEntry
from memory.backends.vector_db import VectorDB
from memory.utils.importance import compute_importance, effective_score, reinforce_importance

class LTSMManager:
    def __init__(self, dim):
        self.db = VectorDB(dim)

    def add_entry(self, id, vector, metadata, decay_rate=0.001):
        now = time.time()
        metadata = metadata or {}
        importance_score = metadata.get(
            "importance",
            compute_importance(
                metadata.get("signals", {}).get("emotion", 0.0),
                metadata.get("signals", {}).get("outcome", 0.0),
                metadata.get("signals", {}).get("reuse", 0.0),
            )
            if metadata.get("signals")
            else 0.0
        )
        metadata["importance"] = importance_score

        entry = MemoryEntry(
            id=id,
            content=metadata.get("content", ""),
            embedding=vector,
            type=metadata.get("type", "ltsm"),
            tags=metadata.get("tags", []),
            importance=importance_score,
            confidence=metadata.get("confidence", 0.0),
            created_at=now,
            last_accessed=now,
            decay_rate=decay_rate,
            source=metadata.get("source", "ltsm"),
            linked_memories=metadata.get("lined_memories", []),
            metadata=metadata
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
        for entry in list(self.db.entries.values()):
            age = now - entry.last_accessed
            if entry.decay_rate > 0 and age > (1 / entry.decay_rate):
                del self.db.entries[entry.id]