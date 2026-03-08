import sqlite3
from memory.core.schema import MemoryEntry
from cryptography.fernet import Fernet
import json
from typing import List

def get_cipher() -> Fernet:
    """Load the Fernet cipher for encryption/decryption."""
    with open("fernet.key", "rb") as f:
        key = f.read()
    return Fernet(key)

def get_connection() -> sqlite3.Connection:
    """Get a new SQLite connection."""
    return sqlite3.connect('memory.db')

def init_db() -> None:
    """Initialize the memories table if it does not exist."""
    with get_connection() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            encrypted_entry BLOB,
            content TEXT,
            importance REAL,
            decay_rate REAL,
            tags TEXT,
            created_at REAL,
            last_accessed REAL
        )
        ''')
        conn.commit()

def add_memory(entry: MemoryEntry) -> None:
    """Add a memory entry to the database."""
    cipher = get_cipher()
    data = json.dumps(entry.__dict__).encode("utf-8")
    encrypted = cipher.encrypt(data)
    tags_str = ','.join(entry.tags)
    encrypted_tags = cipher.encrypt(tags_str.encode("utf-8"))
    with get_connection() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO memories (id, encrypted_entry, content, importance, decay_rate, tags, created_at, last_accessed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (
                entry.id,
                encrypted,
                entry.content,
                entry.importance,
                entry.decay_rate,
                encrypted_tags,
                entry.created_at,
                entry.last_accessed
            )
        )
        conn.commit()

def load_memories() -> List[MemoryEntry]:
    """Load all memory entries from the database."""
    cipher = get_cipher()
    memories = []
    with get_connection() as conn:
        cursor = conn.execute('SELECT id, encrypted_entry FROM memories')
        for row in cursor.fetchall():
            decrypted = cipher.decrypt(row[1])
            entry_dict = json.loads(decrypted.decode("utf-8"))
            entry = MemoryEntry(**entry_dict)
            memories.append(entry)
    return memories

def delete_memory(memory_id: str) -> None:
    """Delete a memory entry by ID."""
    with get_connection() as conn:
        conn.execute('DELETE FROM memories WHERE id=?', (memory_id,))
        conn.commit()

# Initialize the database table on module load
init_db()