from __future__ import annotations
import time
import hashlib
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import numpy as np
from math import exp

from memory.backends.chroma_db import add_memory, query_memory
from memory.utils.importance import compute_importance, effective_score
from memory.utils.decay import decay_score
from memory.utils.reader import get_memories_by_tag, get_memories_by_type
from memory.utils.writer import save_memory, delete_memory

if TYPE_CHECKING:
    from memory.managers.ltsm import LTSMManager

class MemoryAPI:
    """
    High-level API for querying, scoring, and explaining memory entries.
    """
    def __init__(self, ltsm: Optional["LTSMManager"] = None):
        self.ltsm = ltsm

    def query(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        time_window: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query memories with optional tag and time filtering, returning scored/explained results.
        Uses cosine similarity between the query and memory embeddings.
        """
        def cosine_similarity(a, b):
            a = np.array(a)
            b = np.array(b)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
            
        cutoff = None
        if time_window:
            units = {"month": 30*24*3600, "months": 30*24*3600, "day": 24*3600, "days": 24*3600}
            parts = time_window.split()
            if len(parts) == 2 and parts[1] in units:
                cutoff = time.time() - int(parts[0]) * units[parts[1]]

        if not self.ltsm:
            return []
        query_vec = _deterministic_embed(query, dim=getattr(self.ltsm, "dim", 8))

        results = self.ltsm.read(query, top_k=top_k, tag_filter=tags)
        explained = []
        scores = []
        now = time.time()
        for entry in results:
            if cutoff and entry.created_at < cutoff:
                continue
            similarity = cosine_similarity(query_vec, entry.embedding)
            importance = entry.importance
            age_days = (now - entry.created_at) / (60 * 60 * 24)
            final_score = decay_score(importance, age_days)
            scores.append(final_score)
            explained.append({
                "content": entry.content,
                "why_selected": f"Similarity={similarity:.3f}, Importance={importance:.3f}, AgeDays={age_days:.3f}",
                "confidence_score": final_score,
                "metadata": {
                    "tags": entry.tags,
                    "created_at": entry.created_at,
                    "last_accessed": entry.last_accessed,
                }
            })
        max_score = max(scores) if scores else 1.0
        for e in explained:
            e["confidence_score"] = e["confidence_score"] / max_score if max_score > 0 else 0.0
        return explained

    def timeline(
        self,
        tags: Optional[List[str]] = None,
        time_window: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Return a timeline of memories, optionally filtered by tags and time window.
        """
        cutoff = None
        if time_window:
            units = {"month": 30*24*3600, "months": 30*24*3600, "day": 24*3600, "days": 24*3600}
            parts = time_window.split()
            if len(parts) == 2 and parts[1] in units:
                cutoff = time.time() - int(parts[0]) * units[parts[1]]

        if not self.ltsm:
            return []

        all_entries = list(self.ltsm.db.entries.values())
        filtered = []
        for entry in all_entries:
            if tags and not any(t in entry.tags for t in tags):
                continue
            if cutoff and entry.created_at < cutoff:
                continue
            filtered.append(entry)
        filtered.sort(key=lambda e: e.created_at)
        return [
            {
                "id": e.id,
                "content": e.content,
                "tags": e.tags,
                "created_at": e.created_at,
                "importance": e.importance,
                "decay_rate": e.decay_rate,
                "last_accessed": e.last_accessed,
            }
            for e in filtered
        ]

    def influences(self, decision_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Return memories influencing a given decision.
        """
        return self.query(query=decision_id, top_k=top_k)

    def get_memory_history(self, memory_id: str) -> Dict[str, Any]:
        """
        Return the history of a memory entry, if available.
        History is stored in the entry's metadata['history'] list.
        """
        if not self.ltsm or not hasattr(self.ltsm, "db"):
            return {}

        entry = self.ltsm.db.entries.get(memory_id)
        if not entry:
            return {}

        history = entry.metadata.get("history", [])
        # Always include the current state as the latest event
        current_state = {
            "content": entry.content,
            "created_at": entry.created_at,
            "last_accessed": entry.last_accessed,
            "importance": entry.importance,
            "decay_rate": entry.decay_rate,
            "tags": entry.tags,
            "timestamp": time.time(),
            "event": "current_state"
        }
        return {
            "id": entry.id,
            "history": history + [current_state]
        }

    def _compute_decay_curve(self, entry, points: int = 20) -> List[Dict[str, float]]:
        """
        Compute a decay curve for a memory entry.
        """
        now = time.time()
        curve = []
        for i in range(points):
            t = entry.created_at + i * (now - entry.created_at) / points
            dt = (now - t) / 60.0
            score = entry.importance * exp(-entry.decay_rate * dt)
            curve.append({"timestamp": t, "score": score})
        return curve

    def why_chain(self, memory_id: str, depth: int = 2) -> Dict[str, Any]:
        """
        Recursively explain why a memory was selected, by following its 'influences' in metadata.
        """
        if not self.ltsm or not hasattr(self.ltsm, "db") or depth <= 0:
            return {}

        entry = self.ltsm.db.entries.get(memory_id)
        if not entry:
            return {}

        influences = entry.metadata.get("influences", [])
        return {
            "id": entry.id,
            "content": entry.content,
            "tags": entry.tags,
            "created_at": entry.created_at,
            "importance": entry.importance,
            "decay_rate": entry.decay_rate,
            "last_accessed": entry.last_accessed,
            "influences": [
                self.why_chain(inf_id, depth - 1) for inf_id in influences
            ] if influences and depth > 1 else []
        }

    def delete_memories(self, tag: Optional[str] = None, content_match: Optional[str] = None) -> int:
        """
        Delete memories by tag or content match.
        Returns the number of deleted entries.
        """
        if not self.ltsm or not hasattr(self.ltsm, "db"):
            return 0
    
        to_delete = []
        for mem_id, entry in list(self.ltsm.db.entries.items()):
            tag_match = tag and tag in entry.tags
            content_match_found = content_match and content_match in entry.content
            if tag_match or content_match_found:
                to_delete.append(mem_id)
    
        for mem_id in to_delete:
            delete_memory(mem_id)
            # Optionally, also remove from in-memory index if needed:
            self.ltsm.db.entries.pop(mem_id, None)
    
        return len(to_delete)

# --- Utility Functions ---

def summarize(event: Any) -> str:
    """
    Summarize an event for storage.
    """
    if isinstance(event, dict):
        if "text" in event:
            return str(event["text"])[:1000]
        return " ".join(f"{k}:{v}" for k, v in event.items())[:1000]
    return str(event)[:1000]

def classify_tags(event: Any) -> List[str]:
    """
    Classify tags for an event.
    """
    tags: List[str] = []
    if isinstance(event, dict):
        if "decision" in event:
            tags.append("decision")
        if "emotion" in event:
            tags.append("emotion")
        if event.get("success") is True:
            tags.append("success")
        if event.get("failure") is True:
            tags.append("failure")
        if "tags" in event and isinstance(event["tags"], list):
            tags.extend([str(t) for t in event["tags"]])
    return list(dict.fromkeys([t.lower() for t in tags]))

def _deterministic_embed(text: str, dim: int = 8) -> List[float]:
    """
    Deterministically embed text into a fixed-size vector.
    """
    h = hashlib.sha256(text.encode("utf-8")).digest()
    needed = dim * 4
    rep = (h * ((needed // len(h)) + 1))[:needed]
    arr = np.frombuffer(rep, dtype=np.uint8).astype(np.float32)
    arr = arr.reshape(dim, 4).sum(axis=1)
    arr = (arr - arr.mean()) / (arr.std() + 1e-9)
    return arr.tolist()

def estimate_importance_from_signals(signals: Optional[Dict[str, float]]) -> float:
    """
    Estimate importance from signals.
    """
    if not signals:
        return 0.5
    return compute_importance(
        float(signals.get("emotion", 0.0)),
        float(signals.get("outcome", 0.0)),
        float(signals.get("reuse", 0.0)),
    )

def write_memory(
    event: Any,
    dim: int = 8,
    id: Optional[str] = None,
    signals: Optional[Dict[str, float]] = None,
    decay_rate: float = 0.001,
) -> str:
    """
    Write a memory event to storage.
    """
    summary = summarize(event)
    tags = classify_tags(event)
    importance = estimate_importance_from_signals(signals or (event.get("signals") if isinstance(event, dict) else None))

    if id is None:
        short = hashlib.md5(summary.encode("utf-8")).hexdigest()[:8]
        id = f"mem-{int(time.time()*1000)}-{short}"

    metadata = {
        "content": summary,
        "tags": tags,
        "importance": importance,
        "signals": signals or (event.get("signals") if isinstance(event, dict) else {}),
        "timestamp": time.time(),
        "decay_rate": decay_rate,
        "last_accessed": time.time(),
    }

    add_memory(id, summary, metadata)
    return id

def read_memory(
    query: Any,
    ltsm: "LTSMManager",
    top_k: int = 5,
    type_filter: Optional[List[str]] = None,
    tag_filter: Optional[List[str]] = None,
) -> List[Any]:
    """
    Read memories using vector search and filter.
    """
    if isinstance(query, str):
        qvec = _deterministic_embed(query, dim=getattr(ltsm, "dim", 8))
    else:
        qvec = query

    vec = ltsm.db._prepare_vector(qvec)
    D, I = ltsm.db.index.search(vec, top_k)
    now = time.time()

    id_to_key = getattr(ltsm.db, "_id_to_key", None)
    keys_fallback = list(ltsm.db.entries.keys()) if id_to_key is None else None

    candidates = []
    for dist, idx in zip(D[0], I[0]):
        idx_int = int(idx)
        if idx_int == -1:
            continue

        if id_to_key is not None:
            key = id_to_key.get(idx_int)
        else:
            key = keys_fallback[idx_int] if 0 <= idx_int < len(keys_fallback) else None

        if key is None:
            continue

        entry = ltsm.db.entries.get(key)
        if entry is None:
            continue

        if type_filter and entry.type not in type_filter:
            continue
        if tag_filter and not any(t in entry.tags for t in tag_filter):
            continue

        try:
            similarity = 1.0 / (1.0 * float(dist))
        except Exception:
            similarity = 0.0

        imp_decay = effective_score(entry.importance, entry.decay_rate, timestamp=entry.last_accessed, now_ts=now)
        final_score = similarity * float(imp_decay)

        candidates.append((final_score, entry))

    candidates.sort(key=lambda x: x[0], reverse=True)
    results = [e for _, e in candidates[:top_k]]

    for e in results:
        e.last_accessed = now

    return results