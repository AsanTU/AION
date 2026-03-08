import chromadb
from chromadb.config import Settings
from memory.utils.embedding import embed_text
from typing import Optional, Dict, Any, List

# Singleton ChromaDB client and collection
_chroma_client = None
_collection = None

def get_chroma_collection() -> chromadb.api.models.Collection:
    """Get or create the singleton ChromaDB collection for memories."""
    global _chroma_client, _collection
    if _chroma_client is None:
        _chroma_client = chromadb.Client(Settings(persist_directory="./chroma_db"))
    if _collection is None:
        _collection = _chroma_client.get_or_create_collection("memories")
    return _collection

def add_memory(
    id: str,
    text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Add a single memory to the ChromaDB collection.
    """
    collection = get_chroma_collection()
    embedding = embed_text(text)
    collection.add(
        ids=[id],
        embeddings=[embedding],
        metadatas=[metadata or {}],
        documents=[text]
    )

def add_memories(
    ids: List[str],
    texts: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None
) -> None:
    """
    Add multiple memories in a batch.
    """
    collection = get_chroma_collection()
    embeddings = [embed_text(text) for text in texts]
    metadatas = metadatas or [{} for _ in texts]
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=texts
    )

def query_memory(
    query_text: str,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Query the ChromaDB collection for the most relevant memories.
    Returns a dict with keys: 'ids', 'documents', 'embeddings', 'metadatas', 'distances'.
    """
    collection = get_chroma_collection()
    embedding = embed_text(query_text)
    return collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )