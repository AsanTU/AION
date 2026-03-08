from typing import Dict, Optional, List, Any
import threading
import time
from datetime import datetime, timedelta, timezone

from memory.utils.importance import compute_importance, effective_score, reinforce_importance
from memory.core.schema import MemoryEntry
from memory.api import summarize, classify_tags, estimate_importance_from_signals, _deterministic_embed
from memory.storage.sqlite_storage import load_memories, add_memory, delete_memory

class ShortTermMemory:
    """
    Manages short-term (semantic) memories with TTL and automatic eviction.
    """
    def __init__(self, eviction_interval: int = 60, start_eviction_thread: bool = True):
        self.store: Dict[str, MemoryEntry] = {
            entry.id: entry
            for entry in load_memories()
            if getattr(entry, "type", None) == "semantic"
        }
        self._lock = threading.Lock()
        self._eviction_interval = eviction_interval
        self._stop_event = threading.Event()
        if start_eviction_thread:
            self._eviction_thread = threading.Thread(target=self._evict_expired_entries, daemon=True)
            self._eviction_thread.start()

    def set(
        self,
        key: str,
        content: str,
        ttl_minutes: int = 10,
        source: str = "system",
        priority: int = 3,
        importance: float = 0.5,
        confidence: float = 0.5,
        tags: Optional[List[str]] = None,
        signals: Optional[dict] = None,
        dim: int = 8
    ) -> None:
        now = time.time()
        summary = summarize({"text": content}) if content else summarize({})
        pipeline_tags = classify_tags({"text": content, "tags": tags or []})
        importance_score = (
            estimate_importance_from_signals(signals)
            if signals is not None
            else importance
        )
        embedding = _deterministic_embed(summary, dim=dim)
        expires_at = now + ttl_minutes * 60

        entry = MemoryEntry(
            id=key,
            content=summary,
            embedding=embedding,
            type="semantic",
            tags=pipeline_tags,
            importance=importance_score,
            confidence=confidence,
            created_at=now,
            last_accessed=now,
            decay_rate=0.01,
            source=source,
            linked_memories=[],
            metadata={
                "priority": priority,
                "expires_at": expires_at,
                "importance": importance_score,
                "decay_rate": 0.01,
                "signals": signals or {},
            }
        )
        with self._lock:
            self.store[key] = entry
        add_memory(entry)

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            entry = self.store.get(key)
            if not entry:
                return None
            expires_at = entry.metadata.get("expires_at")
            if expires_at and time.time() > expires_at:
                del self.store[key]
                return None
            imp = entry.metadata.get("importance", 0.0)
            decay = entry.metadata.get("decay_rate", entry.decay_rate)
            ts = entry.last_accessed or entry.created_at
            if effective_score(imp, decay, timestamp=ts) < 0.01:
                del self.store[key]
                return None
            return entry.content

    def reinforce(self, key: str, reinforcement: dict, boost: float = 0.05) -> None:
        now = time.time()
        with self._lock:
            entry = self.store.get(key)
            if not entry:
                return
            current = entry.metadata.get("importance", 0.0)
            new_imp = reinforce_importance(current, reinforcement, boost=boost)
            entry.metadata["importance"] = new_imp
            entry.last_accessed = now
        add_memory(entry)

    def cleanup(self) -> None:
        now = time.time()
        with self._lock:
            expired_keys = []
            for k, v in self.store.items():
                expires_at = v.metadata.get("expires_at")
                if expires_at and now > expires_at:
                    expired_keys.append(k)
                    continue
                imp = v.metadata.get("importance", 0.0)
                decay = v.metadata.get("decay_rate", v.decay_rate)
                ts = v.last_accessed or v.created_at
                if effective_score(imp, decay, timestamp=ts) < 0.01:
                    expired_keys.append(k)
            for k in expired_keys:
                del self.store[k]
                delete_memory(k)

    def _evict_expired_entries(self) -> None:
        while not self._stop_event.is_set():
            self.cleanup()
            time.sleep(self._eviction_interval)

    def stop_eviction(self) -> None:
        self._stop_event.set()
        self._eviction_thread.join()

    def set_ltsm(self, ltsm) -> None:
        self.ltsm = ltsm

    def semantic_query(
        self,
        query: str,
        top_k: int = 5,
        type_filter: Optional[List[str]] = None,
        tag_filter: Optional[List[str]] = None,
        ltsm: Optional[Any] = None
    ) -> List[Any]:
        ltsm = ltsm or getattr(self, "ltsm", None)
        if ltsm is None:
            return []
        return ltsm.read(query, top_k=top_k, type_filter=type_filter, tag_filter=tag_filter)