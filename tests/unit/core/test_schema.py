import time
import pytest
from memory.core.schema import MemoryEntry

def test_memory_entry_creation_defaults():
    entry = MemoryEntry(id="1", content="test")
    assert entry.id == "1"
    assert entry.content == "test"
    assert entry.type == "semantic"
    assert entry.tags == []
    assert entry.importance == 0.0
    assert entry.confidence == 0.0
    assert isinstance(entry.created_at, float)
    assert isinstance(entry.last_accessed, float)
    assert entry.decay_rate == 0.0
    assert entry.source == "system"
    assert entry.linked_memories == []
    assert entry.metadata == {}
    assert entry.visibility == "public"

def test_update_access_time():
    entry = MemoryEntry(id="2", content="access")
    old_time = entry.last_accessed
    time.sleep(0.01)
    entry.update_access_time()
    assert entry.last_accessed > old_time

def test_add_tag():
    entry = MemoryEntry(id="3", content="tag")
    entry.add_tag("foo")
    assert "foo" in entry.tags
    # Should not duplicate tags
    entry.add_tag("foo")
    assert entry.tags.count("foo") == 1

def test_add_linked_memory():
    entry = MemoryEntry(id="4", content="link")
    entry.add_linked_memory("mem-123")
    assert "mem-123" in entry.linked_memories
    # Should not duplicate links
    entry.add_linked_memory("mem-123")
    assert entry.linked_memories.count("mem-123") == 1

def test_custom_fields():
    entry = MemoryEntry(
        id="5",
        content="custom",
        embedding=[0.1, 0.2],
        type="episodic",
        tags=["a", "b"],
        importance=0.9,
        confidence=0.8,
        decay_rate=0.01,
        source="user",
        linked_memories=["x"],
        metadata={"foo": "bar"},
        visibility="private"
    )
    assert entry.embedding == [0.1, 0.2]
    assert entry.type == "episodic"
    assert entry.tags == ["a", "b"]
    assert entry.importance == 0.9
    assert entry.confidence == 0.8
    assert entry.decay_rate == 0.01
    assert entry.source == "user"
    assert entry.linked_memories == ["x"]
    assert entry.metadata == {"foo": "bar"}
    assert entry.visibility == "private"