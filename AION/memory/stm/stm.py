from datetime import datetime, timedelta
from typing import Dict

from .models import STMEntry

class ShortTermMemory:
    def __init__(self):
        self.store: Dict[str, STMEntry] = {}

    def set(self, key, value, ttl_minutes=10, source="system", priority=3):
        now = datetime.utcnow()
        entry = STMEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes),
            source=source,
            priority=priority
        )
        self.store[key] = entry
    
    def get(self, key):
        entry = self.store.get(key)
        if not entry:
            return None
        
        if datetime.utcnow() > entry.expires_at:
            del self.store[key]
            return None

        return entry.value