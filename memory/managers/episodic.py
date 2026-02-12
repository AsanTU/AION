from typing import List
from datetime import datetime
import uuid

from memory.core.schema import MemoryEntry

class EpisodicMemory:
    def __init__(self):
        self.entries: List[MemoryEntry] = []
    
    def add_entry(self, situation, decisioin, outcome, confidence, tags=None, timestamp=None):
        ts = timestamp or datetime.now().isoformat()
        entry_id = f"episodic-{uuid.uuid4().hex}"
        entry = MemoryEntry(
            id=entry_id,
            content=situation,
            embedding=[],
            type="episodic",
            tags=tags or [],
            importance=0.0,
            confidence=confidence,
            created_at=ts,
            decay_rate=0.0,
            source="episodic",
            linked_memories=[],
            metadata={"decision": decisioin, "outcome": outcome, "timestamp": ts}
        )
        entry.decision = decisioin
        entry.outcome = outcome

        self.entries.append(entry)

    def get_all(self):
        return self.entries
    
    def find_by_tag(self, tag):
        return [e for e in self.entries if tag in e.tags]