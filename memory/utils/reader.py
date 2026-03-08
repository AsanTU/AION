from typing import List, Optional
from memory.core.schema import MemoryEntry

def get_memories_by_tag(memories: List[MemoryEntry], tag: str) -> List[MemoryEntry]:
    """Return all memories with a given tag."""
    return [m for m in memories if tag in m.tags]

def get_memories_by_type(memories: List[MemoryEntry], mem_type: str) -> List[MemoryEntry]:
    """Return all memories of a given type."""
    return [m for m in memories if m.type == mem_type]

def get_recent_memories(memories: List[MemoryEntry], n: int = 10) -> List[MemoryEntry]:
    """Return the n most recently accessed memories."""
    return sorted(memories, key=lambda m: m.last_accessed, reverse=True)[:n]