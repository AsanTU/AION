import sqlite3

conn = sqlite3.connect("agent_metrics.db")
conn.execute('''
CREATE TABLE IF NOT EXISTS agent_metrics (
    agent_name TEXT,
    timestamp REAL,
    performance_score REAL,
    failure_reason TEXT,
    confidence REAL
)
''')
conn.commit()