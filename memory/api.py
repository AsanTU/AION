from __future__ import annotations
import time
import hashlib
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import numpy as np

from memory.utils.importance import compute_importance, effective_score

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
        ltsm: LTSMManager,
        dim: int = 8, 
        id: Optional[str] = None,
        signals: Optional[Dict[str, float]] = None,
        decay_rate: float = 0.001,
) -> str:
    summary = summarize(event)
    tags = classify_tags(event)
    importance = estimate_importance_from_signals(signals or event.get("signals") if isinstance(event, dict) else None)
    embedding = _deterministic_embed(summary, dim=dim)

    if id is None:
        short = hashlib.md5(summary.encode("utf-8")).hexdigest()[:8]
        id = f"mem-{int(time.time()*1000)}-{short}"

    metadata = {
        "content": summary,
        "tags": tags,
        "importance": importance,
        "signals": signals or event.get("signals") if isinstance(event, dict) else {},
        "timestamp": time.time(),
    }

    ltsm.add_entry(id, embedding, metadata, decay_rate=decay_rate)
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
    keys = list(ltsm.db.entries.keys())
    now = time.time()

    candidates = []
    for dist, idx in zip(D[0], I[0]):
        if idx == -1:
            continue
        key = keys[idx]
        entry = ltsm.db.entries.get(key)
        if entry is None:
            continue

        if type_filter and entry.type not in type_filter:
            continue
        if tag_filter and not any(t in entry.tags for t in tag_filter):
            continue

        similarity = 1.0 / (1.0 * float(dist))
        imp_decay = effective_score(entry.importance, entry.decay_rate, timestamp=entry.last_accessed, now_ts=now)
        final_score = similarity * float(imp_decay)

        candidates.append((final_score, entry))

    candidates.sort(key=lambda x: x[0], reverse=True)
    results = [e for _, e in candidates[:top_k]]

    for e in results:
        e.last_accessed = now

    return results