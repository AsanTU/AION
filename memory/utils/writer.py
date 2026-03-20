from memory.core.schema import MemoryEntry
from memory.storage.sqlite_storage import add_memory, delete_memory

def save_memory(entry: MemoryEntry) -> None:
    """Save a memory entry to storage."""
    add_memory(entry)

def update_memory(entry: MemoryEntry, **kwargs) -> None:
    """Update fields of a memory entry and save."""
    for key, value in kwargs.items():
        if hasattr(entry, key):
            setattr(entry, key, value)
    add_memory(entry)

def batch_save_memories(entries: list[MemoryEntry]) -> None:
    """Save multiple memory entries at once."""
    for entry in entries:
        add_memory(entry)