from datetime import datetime, timedelta, UTC
from typing import Dict
import threading
import time
from memory.utils.importance import compute_importance, effective_score, reinforce_importance

from memory.core.schema import MemoryEntry
from memory.api import summarize, classify_tags, estimate_importance_from_signals, _deterministic_embed

class ShortTermMemory:
    def __init__(self, eviction_interval=60, start_eviction_thread=True):
        self.store: Dict[str, MemoryEntry] = {}
        self._lock = threading.Lock()
        self._eviction_interval = eviction_interval
        self._stop_event = threading.Event()
        if start_eviction_thread:
            self._eviction_thread = threading.Thread(target=self._evict_expired_entries, daemon=True)
            self._eviction_thread.start()

    def set(self, key, content, ttl_minutes=10, source="system", priority=3, importance=0.5, confidence=0.5, tags=None, signals=None, dim: int = 8):
        now = datetime.now(UTC)

        summary = summarize({"text": content}) if content else summarize({})
        pipeliine_tags = classify_tags({"text": content, "tags": tags or []})
        importance_score = (
            estimate_importance_from_signals(signals)
            if signals is not None
            else importance
        )
        embedding = _deterministic_embed(summary, dim=dim)

        entry = MemoryEntry(
            id=key,
            content=summary,
            embedding=embedding, 
            type="semantic",
            tags=pipeliine_tags,
            importance=importance_score,
            confidence=confidence,
            created_at=now.isoformat(),
            last_accessed=now.isoformat(),
            decay_rate=0.01,
            source=source,
            linked_memories=[],
            metadata={"priority": priority, "expires_at": (now + timedelta(minutes=ttl_minutes)).isoformat(), "importance": importance_score, "decay_rate": 0.01, "signals": signals or {},}
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
            imp = entry.metadata.get("importance", 0.0)
            decay = entry.metadata.get("decay_rate", entry.decay_rate)
            ts = entry.last_accessed or entry.created_at
            if effective_score(imp, decay, timestamp=ts) < 0.01:
                del self.store[key]
                return None
            return entry.content
        
    def reinforce(self, key, reinforcement: dict, boost: float = 0.05):
        now = datetime.now(UTC).isoformat()
        with self._lock:
            entry = self.store.get(key)
            if not entry:
                return
            current = entry.metadata.get("importance", 0.0)
            new_imp = reinforce_importance(current, reinforcement, boost=boost)
            entry.metadata["importance"] = new_imp
            entry.last_accessed = now
        
    def cleanup(self):
        now = datetime.now(UTC)
        with self._lock:
            expired_keys = []
            for k, v in self.store.items():
                expires_at = v.metadata.get("expires_at")
                if expires_at and now > datetime.fromisoformat(expires_at):
                    expired_keys.append(k)
                    continue
                imp = v.metadata.get("importance", 0.0)
                decay = v.metadata.get("decay_rate", v.decay_rate)
                ts = v.last_accessed or v.created_at
                if effective_score(imp, decay, timestamp=ts) < 0.01:
                    expired_keys.append(k)
            for k in expired_keys:
                del self.store[k]
    
    def _evict_expired_entries(self):
        while not self._stop_event.is_set():
            self.cleanup()
            time.sleep(self._eviction_interval)

    def stop_eviction(self):
        self._stop_event.set()
        self._eviction_thread.join()