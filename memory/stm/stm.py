from datetime import datetime, timedelta, UTC
from typing import Dict
import threading
import time

from memory.schema import MemoryEntry

class ShortTermMemory:
    def __init__(self, eviction_interval=60, start_eviction_thread=True):
        self.store: Dict[str, MemoryEntry] = {}
        self._lock = threading.Lock()
        self._eviction_interval = eviction_interval
        self._stop_event = threading.Event()
        if start_eviction_thread:
            self._eviction_thread = threading.Thread(target=self._evict_expired_entries, daemon=True)
            self._eviction_thread.start()

    def set(self, key, content, ttl_minutes=10, source="system", priority=3, importance=0.5, confidence=0.5, tags=None):
        now = datetime.now(UTC)
        entry = MemoryEntry(
            id=key,
            content=content,
            embedding=[], 
            type="semantic",
            tags=tags or [],
            importance=importance,
            confidence=confidence,
            created_at=now.isoformat(),
            last_accessed=now.isoformat(),
            decay_rate=0.01,
            source=source,
            linked_memories=[],
            metadata={"priority": priority, "expires_at": (now + timedelta(minutes=ttl_minutes)).isoformat()}
        )
        with self._lock:
            self.store[key] = entry
    
    def get(self, key):
        with self._lock:
            entry = self.store.get(key)
            if not entry:
                return None
            expires_at = entry.metadata.get("expires_at")
            if expires_at and datetime.now(UTC) > datetime.fromisoformat(expires_at):
                del self.store[key]
                return None
            return entry.content
        
    def cleanup(self):
        now = datetime.now(UTC)
        with self._lock:
            expired_keys = [
                k for k, v in self.store.items()
                if v.metadata.get("expires_at") and now > datetime.fromisoformat(v.metadata["expires_at"])
            ]
            for k in expired_keys:
                del self.store[k]
    
    def _evict_expired_entries(self):
        while not self._stop_event.is_set():
            self.cleanup()
            time.sleep(self._eviction_interval)

    def stop_eviction(self):
        self._stop_event.set()
        self._eviction_thread.join()