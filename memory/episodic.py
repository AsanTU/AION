from typing import List
from datetime import datetime

from memory.schema import EpisodicMemoryEntry

class EpisodicMemory:
    def __init__(self):
        self.entries: List[EpisodicMemoryEntry] = []
    
    def add_entry(self, situation, decisioin, outcome, confidence, tags=None, timestamp=None):
        entry = EpisodicMemoryEntry(
            situation=situation,
            decision=decisioin,
            outcome=outcome,
            confidence=confidence,
            timestamp=timestamp or datetime.now().isoformat(),
            tags=tags or []
        )
        self.entries.append(entry)

    def get_all(self):
        return self.entries
    
    def find_by_tag(self, tag):
        return [e for e in self.entries if tag in e.tags]