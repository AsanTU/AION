import time
from memory.core.schema import MemoryEntry
from memory.backends.vector_db import VectorDB
from memory.utils.importance import compute_importance, effective_score, reinforce_importance
from memory.api import write_memory
from memory.storage.sqlite_storage import load_memories, add_memory, delete_memory

class LTSMManager:
    def __init__(self, dim):
        self.db = VectorDB(dim)
        self.dim = dim
        self.entries = {entry.id: entry for entry in load_memories()}

    def add_entry(self, id, vector, metadata, decay_rate=0.001):
        now = time.time()
        metadata = metadata or {}
        if metadata.get("signals"):
            importance_score = compute_importance(
                metadata["signals"].get("emotion", 0.0),
                metadata["signals"].get("outcome", 0.0),
                metadata["signals"].get("reuse", 0.0),
            )
        else:
            importance_score = float(metadata.get("importance", 0.0))

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
        self.entries[entry.id] = entry
        add_memory(entry)

    def write(self, event, id: str | None = None, signals: dict | None = None, decay_rate: float | None = None):
        decay_rate = decay_rate if decay_rate is not None else 0.001
        from memory.api import write_memory
        return write_memory(event, self, dim=self.dim, id=id, signals=signals, decay_rate=decay_rate)

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

    def read(self, query, top_k: int = 5, type_filter: list | None = None, tag_filter: list | None = None):
        from memory.api import read_memory
        return read_memory(query, self, top_k=top_k, type_filter=type_filter, tag_filter=tag_filter)
    
    def delete_entry(self, memory_id):
        if memory_id in self.entries:
            del self.entries[memory_id]
            delete_memory(memory_id)