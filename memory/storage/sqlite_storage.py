import sqlite3
from memory.core.schema import MemoryEntry

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
    conn.execute(
        'INSERT INTO memories (id, content, decay_rate, tags, created_at, last_accessed) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (entry.id, entry.content, entry.importance, entry.decay_rate, ','.join(entry.tags), entry.created_at, entry.last_accessed)
    )
    conn.commit()   

def load_memories():
    cursor = conn.execute('SELECT id, content, importance, decay_rate, tags, created_at, last_accessed FROM memories')
    memories = []
    for row in cursor.fetchall():
        entry = MemoryEntry(
            id=row[0],
            content=row[1],
            importance=row[2],
            decay_rate=row[3],
            tags=row[4].split(','),
            created_at=row[5],
            last_accessed=[6]
        )
        memories.append(entry)
    return memories

def delete_memory(memory_id):
    conn.execute('DELETE FROM memories WHERE id=?', (memory_id))
    conn.commit()