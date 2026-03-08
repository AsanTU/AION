import time
from typing import Dict, List, Optional, Any
from memory.core.schema import MemoryEntry
from memory.backends.vector_db import VectorDB
from memory.utils.importance import compute_importance
from memory.storage.sqlite_storage import load_memories, delete_memory
from memory.utils.writer import save_memory, batch_save_memories
from memory.utils.reader import get_memories_by_tag, get_memories_by_type, get_recent_memories

class LTSMManager:
    """
    Long-Term Semantic Memory (LTSM) manager using a vector database.
    """
    def __init__(self, dim: int):
        self.db = VectorDB(dim)
        self.dim = dim
        self.entries: Dict[str, MemoryEntry] = {entry.id: entry for entry in load_memories()}

    def add_entry(
        self,
        id: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]],
        decay_rate: float = 0.001
    ) -> None:
        """
        Add a new memory entry to the LTSM.
        """
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
            linked_memories=metadata.get("linked_memories", []),
            metadata=metadata
        )
        self.db.add(entry)
        self.entries[entry.id] = entry
        save_memory(entry)

    def add_entries_batch(self, entries_data: List[Dict[str, Any]]) -> None:
        """
        Add multiple memory entries in a batch.
        """
        new_entries = []
        for data in entries_data:
            entry = MemoryEntry(**data)
            self.db.add(entry)
            self.entries[entry.id] = entry
            new_entries.append(entry)
        batch_save_memories(new_entries)

    def write(
        self,
        event: Any,
        id: Optional[str] = None,
        signals: Optional[Dict[str, Any]] = None,
        decay_rate: Optional[float] = None
    ) -> str:
        """
        Write a new memory event using the API's write_memory function.
        """
        decay_rate = decay_rate if decay_rate is not None else 0.001
        from memory.api import write_memory
        return write_memory(event, self, dim=self.dim, id=id, signals=signals, decay_rate=decay_rate)

    def query(self, vector: List[float], top_k: int = 5) -> List[MemoryEntry]:
        """
        Query the vector database for the most similar memories.
        """
        results = self.db.query(vector, top_k)
        now = time.time()
        for entry in results:
            entry.last_accessed = now
        return results

    def decay_entries(self) -> None:
        """
        Remove entries that have decayed past their threshold.
        """
        now = time.time()
        for entry in list(self.db.entries.values()):
            age = now - entry.last_accessed
            if entry.decay_rate > 0 and age > (1 / entry.decay_rate):
                del self.db.entries[entry.id]

    def read(
        self,
        query: Any,
        top_k: int = 5,
        type_filter: Optional[List[str]] = None,
        tag_filter: Optional[List[str]] = None
    ) -> List[Any]:
        """
        Read memories using the API's read_memory function.
        """
        from memory.api import read_memory
        return read_memory(query, self, top_k=top_k, type_filter=type_filter, tag_filter=tag_filter)

    def delete_entry(self, memory_id: str) -> None:
        """
        Delete a memory entry by ID.
        """
        if memory_id in self.entries:
            del self.entries[memory_id]
            delete_memory(memory_id)

    def find_by_tag(self, tag: str) -> List[MemoryEntry]:
        """
        Find LTSM memories by tag.
        """
        return get_memories_by_tag(list(self.entries.values()), tag)

    def find_by_type(self, mem_type: str) -> List[MemoryEntry]:
        """
        Find LTSM memories by type.
        """
        return get_memories_by_type(list(self.entries.values()), mem_type)

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """
        Get the n most recently accessed LTSM memories.
        """
        return get_recent_memories(list(self.entries.values()), n)