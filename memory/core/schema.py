from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time

@dataclass
class MemoryEntry:
    """
    Represents a single memory entry in the system.
    """
    id: str
    content: str
    embedding: List[float] = field(default_factory=list)
    type: str = "semantic"
    tags: List[str] = field(default_factory=list)
    importance: float = 0.0
    confidence: float = 0.0
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    decay_rate: float = 0.0
    source: str = "system"
    linked_memories: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    visibility: str = "public"

    def update_access_time(self) -> None:
        """Update the last accessed timestamp to now."""
        self.last_accessed = time.time()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the memory entry if not already present."""
        if tag not in self.tags:
            self.tags.append(tag)

    def add_linked_memory(self, memory_id: str) -> None:
        """Link another memory entry by its ID."""
        if memory_id not in self.linked_memories:
            self.linked_memories.append(memory_id)