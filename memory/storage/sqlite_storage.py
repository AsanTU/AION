import sqlite3
from memory.core.schema import MemoryEntry
from cryptography.fernet import Fernet

with open("memory.key", "rb") as key_file:
    key = key_file.read()
cipher = Fernet(key)

conn = sqlite3.connect('memory.db')

conn.execute('''
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    content TEXT,
    importance REAL,
    decay_rate REAL,
    tags TEXT,
    created_at REAL,
    last_accessed REAL
)
''')
conn.commit()

def add_memory(entry):
    encrypted_content = cipher.encrypt(entry.content.encode("utf-8"))
    encrypted_tags = cipher.encrypt(','.join(entry.tags).encode("utf-8"))
    conn.execute(
        'INSERT INTO memories (id, content, decay_rate, tags, created_at, last_accessed) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (entry.id, encrypted_content, entry.importance, entry.decay_rate, encrypted_tags, entry.created_at, entry.last_accessed)
    )
    conn.commit()   

def load_memories():
    cursor = conn.execute('SELECT id, content, importance, decay_rate, tags, created_at, last_accessed FROM memories')
    memories = []
    for row in cursor.fetchall():
        decrypted_content = cipher.decrypt(row[1]).decode("utf-8")
        decrypted_tags = cipher.decrypt(row[4]).decode("utf-8").split(',')
        entry = MemoryEntry(
            id=row[0],
            content=decrypted_content,
            importance=row[2],
            decay_rate=row[3],
            tags=decrypted_tags,
            created_at=row[5],
            last_accessed=row[6]
        )
        memories.append(entry)
    return memories

def delete_memory(memory_id):
    conn.execute('DELETE FROM memories WHERE id=?', (memory_id,))
    conn.commit()