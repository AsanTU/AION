from __future__ import annotations
import time
import hashlib
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import numpy as np

from memory.backends.chroma_db import add_memory, query_memory
from memory.utils.importance import compute_importance, effective_score
from memory.utils.decay import decay_score

from typing import List, Optional, Dict, Any
import time 
from math import exp

class MemoryAPI:
    def __init__(self):
        pass

    def query(self, query: str, tags: Optional[List[str]] = None, time_window: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        cutoff = None
        if time_window:
            units = {"month": 30*24*3600, "moths": 30*24*3600, "day": 24*3600, "days": 24*3600}
            parts = time_window.split()
            if len(parts) == 2 and parts[1] in units:
                cutoff = time.time() - int(parts[0]) * units[parts[1]]

        
        results = self.ltsm.read(query, top_k=top_k, tag_filter=tags)
        explained = []
        scores = []
        for entry in results:
            if cutoff and entry.created_at < cutoff:
                continue
            similarity = 1.0
            importance = entry.importance
            created_at = entry.created_at
            now = time.time()
            age_days = (now - created_at) / (60 * 60 * 24)
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
        for i, e in enumerate(explained):
            e["confidence_score"] = e["confidence_score"] / max_score if max_score > 0 else 0.0
        return explained
    
    def timeline(self, tags: Optional[List[str]] = None, time_window: Optional[str] = None) -> List[Dict[str, Any]]:
        results = query_memory("", top_k=1000)
        cutoff = None
        if time_window:
            units = {"month": 30*24*3600, "months": 30*24*3600, "day": 24*3600, "days": 24*3600}
            parts = time_window.split()
            if len(parts) == 2 and parts[1] in units:
                cutoff = time.time() - int(parts[0]) * units[parts[1]]
        
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
        return self.query(query=decision_id, top_k=top_k)
    
    def get_memory_history(self, memory_id: str) -> Dict[str, Any]:
        # entry = self.ltsm.db.entries.get(memory_id)
        # if not entry:
        #     return {}
        # history = {
        #     "content": entry.content,
        #     "created_at": entry.created_at,
        #     "last_accessed": entry.last_accessed,
        #     "importance": entry.importance,
        #     "decay_rate": entry.decay_rate,
        #     "tags": entry.tags,
        #     "reinforcement_events": getattr(entry, "reinforcement_events", []),
        #     "decay_curve": self._compute_decay_curve(entry),        
        # }
        # return history

        # TODO Not directly supported in ChromaDB; you may need to store history in metadata or elsewhere
        return {}

    
    def _compute_decay_curve(self, entry, points=20):
        now = time.time()
        curve = []
        for i in range(points):
            t = entry.created_at + 1 * (now - entry.created_at) / points
            dt = (now - t) / 60.0
            score = entry.importance * exp(-entry.decay_rate * dt)
            curve.append({"timestamp": t, "score": score})
        return curve

    def why_chain(self, memory_id: str, depth: int = 2) -> Dict[str, Any]:
        # entry = self.ltsm.db.entries.get(memory_id)
        # if not entry or depth <= 0:
        #     return {}
        # influences = getattr(entry, "influences", [])
        # return {
        #     "memory": entry.content,
        #     "influences": [
        #         self.why_chain(inf_id, depth - 1) for inf_id in influences
        #     ]
        # }

        # TODO Not directly supported in ChromaDB; you may need to store influences in metadata or elsewhere
        return {}
    
    def delete_memories(self, tag: str = None, content_match: str = None):
        # to_delete = []
        # for mem_id, entry in list(self.ltsm.db.entries.items()):
        #     if (tag and tag in entry.tags) or (content_match and content_match in entry.content):
        #         to_delete.append(mem_id)
        # for mem_id in to_delete:
        #     del self.ltsm.db.entries[mem_id]
        # return len(to_delete)

        # TODO ChromaDB does not support deletion by tag/content natively; you would need to implement this
        return 0

if TYPE_CHECKING:
    from memory.managers.ltsm import LTSMManager

def summarize(event: Any) -> str:
    if isinstance(event, dict):
        if "text" in event:
            return str(event["text"])[:1000]
        return " ".join(f"{k}:{v}" for k, v in event.items())[:1000]
    return str(event)[:1000]

def classify_tags(event: Any) -> List[str]:
    tags: List[str] = []
    if isinstance(event, dict):
        if "decision" in event:
            tags.append("decision")
        if "emotion" in event:
            tags.append("emotion")
        if event.get("success") is True:
            tags.append("success")
        if event.get("failure") is  True:
            tags.append("failure")
        if "tags" in event and isinstance(event["tags"], list):
            tags.extend([str(t) for t in event["tags"]])
    return list(dict.fromkeys([t.lower() for t in tags]))

def _deterministic_embed(text: str, dim: int = 8) -> List[float]:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    needed = dim * 4
    rep = (h * ((needed // len(h)) + 1))[:needed]
    arr = np.frombuffer(rep, dtype=np.uint8).astype(np.float32)
    arr = arr.reshape(dim, 4).sum(axis=1)
    arr = (arr - arr.mean()) / (arr.std() + 1e-9)
    return arr.tolist()

def estimate_importance_from_signals(signals: Optional[Dict[str, float]]) -> float:
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
    summary = summarize(event)
    tags = classify_tags(event)
    importance = estimate_importance_from_signals(signals or event.get("signals") if isinstance(event, dict) else None)

    if id is None:
        short = hashlib.md5(summary.encode("utf-8")).hexdigest()[:8]
        id = f"mem-{int(time.time()*1000)}-{short}"

    metadata = {
        "content": summary,
        "tags": tags,
        "importance": importance,
        "signals": signals or event.get("signals") if isinstance(event, dict) else {},
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