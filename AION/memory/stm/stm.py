from datetime import datetime, timedelta, UTC
from typing import Dict
import threading
import time

from .models import STMEntry

class ShortTermMemory:
    def __init__(self, eviction_interval=60):
        self.store: Dict[str, STMEntry] = {}
        self._lock = threading.Lock()
        self._eviction_interval = eviction_interval
        self._stop_event = threading.Event()
        self._eviction_thread = threading.Thread(target=self._evict_expired_entries, daemon=True)
        self._eviction_thread.start()

    def set(self, key, value, ttl_minutes=10, source="system", priority=3):
        now = datetime.now(UTC)
        entry = STMEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes),
            source=source,
            priority=priority
        )
        with self._lock:
            self.store[key] = entry
    
    def get(self, key):
        with self._lock:
            entry = self.store.get(key)
            if not entry:
                return None
            if datetime.now(UTC) > entry.expires_at:
                del self.store[key]
                return None

            return entry.value
        
    def cleanup(self):
        now = datetime.now(UTC)
        with self._lock:
            expired_keys = [k for k, v in self.store.items() if now > v.expires_at]
            for k in expired_keys:
                del self.store[k]
    
    def _evict_expired_entries(self):
        while not self._stop_event.is_set():
            self.cleanup()
            time.sleep(self._eviction_interval)

    def stop_eviction(self):
        self._stop_event.set()
        self._eviction_thread.join()