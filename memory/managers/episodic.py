from typing import List
from datetime import datetime
import uuid

from memory.core.schema import MemoryEntry
from memory.api import summarize, classify_tags, estimate_importance_from_signals, _deterministic_embed
from memory.storage.sqlite_storage import load_memories, add_memory, delete_memory

class EpisodicMemory:
    def __init__(self):
        self.entries: List[MemoryEntry] = [e for e in load_memories() if getattr(e, "type", None) == "episodic"]
    
    def add_entry(self, situation, decisioin, outcome, confidence, tags=None, timestamp=None, dim: int = 8, signals: dict | None = None):
        ts = timestamp or datetime.now().isoformat()
        summary = summarize({"text": situation})
        pipeline_tags = list(dict.fromkeys((tags or []) + classify_tags({"text": situation})))
        importance = estimate_importance_from_signals(signals)

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
            metadata={"decision": decisioin, "outcome": outcome, "timestamp": ts},
            public_memories = [m for m in self.ltsm.db.entries.values() if m.visibility == "public"]
        )
        entry.decision = decisioin
        entry.outcome = outcome

        self.entries.append(entry)
        add_memory(entry)
    
    def delete_entry(self, entry_id):
        self.entries = [e for e in self.entries if e.id != entry_id]
        delete_memory(entry_id)

    def get_all(self):
        return self.entries
    
    def find_by_tag(self, tag):
        return [e for e in self.entries if tag in e.tags]