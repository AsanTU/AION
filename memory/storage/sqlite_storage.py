import sqlite3
from memory.core.schema import MemoryEntry
from cryptography.fernet import Fernet
import json

def get_cipher():
    with open("fernet.key", "rb") as f:
        key = f.read()
    return Fernet(key)

with open("memory.key", "rb") as key_file:
    key = key_file.read()
cipher = get_cipher()

conn = sqlite3.connect('memory.db')

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

def add_memory(entry: MemoryEntry):
    cipher = get_cipher()
    data = json.dumps(entry.__dict__).encode("utf-8")
    encrypted = cipher.encrypt(data)
    encrypted_tags = cipher.encrypt(','.join(entry.tags).encode("utf-8"))
    conn.execute(
        'INSERT INTO memories (id, encrypted_entry, decay_rate, tags, created_at, last_accessed) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (entry.id, encrypted, entry.importance, entry.decay_rate, encrypted_tags, entry.created_at, entry.last_accessed)
    )
    conn.commit()   

def load_memories():
    cipher = get_cipher()
    cursor = conn.execute('SELECT id, encrypted_entry, importance, decay_rate, tags, created_at, last_accessed FROM memories')
    memories = []
    for row in cursor.fetchall():
        decrypted = cipher.decrypt(row[1])
        entry_dict = json.loads(decrypted.decode("utf-8"))
        entry = MemoryEntry(**entry_dict)
        memories.append(entry)
    return memories

def delete_memory(memory_id):
    conn.execute('DELETE FROM memories WHERE id=?', (memory_id,))
    conn.commit()