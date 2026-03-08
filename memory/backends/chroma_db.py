import chromadb
from chromadb.config import Settings
from memory.utils.embedding import embed_text

chroma_client = chromadb.Client(Settings(
    persist_directory="./chroma_db"
))
collection = chroma_client.get_or_create_collection("memories")

def add_memory(id, text, metadata=None):
    embedding = embed_text(text)
    collection.add(
        ids=[id],
        embeddings=[embedding],
        metadatas=[metadata or {}],
        documents=[text]
    )

def query_memory(query_text, top_k=5):
    embedding = embed_text(query_text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    return results