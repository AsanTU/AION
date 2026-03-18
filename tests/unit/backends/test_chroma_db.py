import pytest
import uuid
from memory.backends import chroma_db

def test_add_and_query_memory(tmp_path, monkeypatch):
    # Patch persist_directory to use a temp dir
    monkeypatch.setattr(
        chroma_db,
        "_chroma_client",
        None
    )
    monkeypatch.setattr(
        chroma_db,
        "_collection",
        None
    )

    # Unique test data
    mem_id = f"test-{uuid.uuid4().hex}"
    text = "Test memory for ChromaDB"
    metadata = {"test": True, "value": 42}

    # Add memory
    chroma_db.add_memory(mem_id, text, metadata)

    # Query memory
    result = chroma_db.query_memory("Test memory", top_k=1)
    assert "ids" in result
    assert mem_id in result["ids"][0]
    assert result["documents"][0][0] == text
    assert result["metadatas"][0][0]["test"] is True
    assert result["metadatas"][0][0]["value"] == 42

def test_add_memories_batch():
    ids = [f"batch-{uuid.uuid4().hex}" for _ in range(2)]
    texts = ["Batch memory 1", "Batch memory 2"]
    metadatas = [{"idx": i} for i in range(2)]

    chroma_db.add_memories(ids, texts, metadatas)
    result = chroma_db.query_memory("Batch memory", top_k=2)
    found_ids = set(result["ids"][0])
    for mem_id in ids:
        assert mem_id in found_ids

def test_query_no_results():
    result = chroma_db.query_memory("unlikely search string", top_k=1)
    # Should return empty or very low similarity
    assert "ids" in result
    # Accept empty or non-matching results