from typing import List, Optional, Dict, Any
import uuid
import time

from memory.core.schema import MemoryEntry
from memory.api import summarize, classify_tags, estimate_importance_from_signals, _deterministic_embed
from memory.storage.sqlite_storage import load_memories, delete_memory
from memory.utils.reader import get_memories_by_tag
from memory.utils.writer import save_memory, batch_save_memories

class EpisodicMemory:
    """
    Manages episodic memories: decisions, situations, and outcomes.
    """
    def __init__(self):
        self.entries: List[MemoryEntry] = [
            e for e in load_memories() if getattr(e, "type", None) == "episodic"
        ]

    def add_entry(
        self,
        situation: str,
        decision: str,
        outcome: str,
        confidence: float,
        tags: Optional[List[str]] = None,
        timestamp: Optional[float] = None,
        dim: int = 8,
        signals: Optional[Dict[str, Any]] = None
    ) -> MemoryEntry:
        """
        Add a new episodic memory entry.
        """
        ts = timestamp or time.time()
        summary = summarize({"text": situation})
        pipeline_tags = list(dict.fromkeys((tags or []) + classify_tags({"text": situation})))
        importance = estimate_importance_from_signals(signals or {})

        entry_id = f"episodic-{uuid.uuid4().hex}"
        embedding = _deterministic_embed(summary, dim=dim)

        entry = MemoryEntry(
            id=entry_id,
            content=situation,
            embedding=embedding,
            type="episodic",
            tags=pipeline_tags,
            importance=importance,
            confidence=confidence,
            created_at=ts,
            decay_rate=0.0,
            source="episodic",
            linked_memories=[],
            metadata={
                "decision": decision,
                "outcome": outcome,
                "timestamp": ts
            }
        )

        self.entries.append(entry)
        save_memory(entry)
        return entry

    def add_entries_batch(self, entries_data: List[Dict[str, Any]], dim: int = 8) -> List[MemoryEntry]:
        """
        Add multiple episodic memory entries in a batch.
        """
        new_entries = []
        for data in entries_data:
            entry = self.add_entry(
                situation=data["situation"],
                decision=data["decision"],
                outcome=data["outcome"],
                confidence=data.get("confidence", 0.0),
                tags=data.get("tags"),
                timestamp=data.get("timestamp"),
                dim=dim,
                signals=data.get("signals")
            )
            new_entries.append(entry)
        batch_save_memories(new_entries)
        return new_entries

    def delete_entry(self, entry_id: str) -> None:
        """
        Delete an episodic memory entry by ID.
        """
        self.entries = [e for e in self.entries if e.id != entry_id]
        delete_memory(entry_id)

    def get_all(self) -> List[MemoryEntry]:
        """
        Get all episodic memory entries.
        """
        return self.entries

    def find_by_tag(self, tag: str) -> List[MemoryEntry]:
        """
        Find episodic memories by tag.
        """
        return get_memories_by_tag(self.entries, tag)