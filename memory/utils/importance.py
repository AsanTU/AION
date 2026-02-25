from __future__ import annotations
from datetime import datetime, timezone
import math
from typing import Union, Dict

def _to_timestamp_secs(ts: Union[str, float, int, None]) -> float:
    if ts is None:
        return datetime.now(timezone.utc).timestamp()
    if isinstance(ts, (float, int)):
        return float(ts)
    if isinstance(ts, datetime):
        dt = ts
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    try:
        dt = datetime.fromisoformat(str(ts))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return datetime.now(timezone.utc).timestamp()

def compute_importance(
        emotion: float,
        outcome: float,
        reuse: float,
        alpha: float = 0.5,
        beta: float = 0.3,
        gamma: float = 0.2,
        clip: bool = True,
) -> float:
    score = alpha * emotion + beta * outcome + gamma * reuse
    if clip:
        return max(0.0, min(1.0, score))
    return score

def effective_score(importance: float, decay_rate: float, timestamp: float | str | None = None, now_ts: float | str | None = None) -> float:
    """
    Compute time-weighted importance.
    decay_rate is per-minute.
    """
    import math
    from datetime import datetime, timezone

    def to_epoch(ts):
        if ts is None:
            return None
        if isinstance(ts, (int, float)):
            return float(ts)
        if isinstance(ts, datetime):
            dt = ts
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        try:
            dt = datetime.fromisoformat(str(ts))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except Exception:
            try:
                return float(ts)
            except Exception:
                return None

    now = to_epoch(now_ts) if now_ts is not None else datetime.now(timezone.utc).timestamp()
    ts = to_epoch(timestamp)
    if ts is None:
        return float(max(0.0, min(1.0, float(importance or 0.0))))

    dt_seconds = max(0.0, float(now) - float(ts))
    dt_minutes = dt_seconds / 60.0
    if decay_rate is None or decay_rate <= 0:
        return float(max(0.0, min(1.0, float(importance or 0.0))))

    eff = (float(importance or 0.0)) * math.exp(-float(decay_rate) * dt_minutes)
    return float(max(0.0, min(1.0, eff)))

def reinforce_importance(
        current_importance: float,
        reinforcement: Dict[str, float],
        alpha: float = 0.5,
        beta: float = 0.3,
        gamma: float = 0.2,
        boost: float = 0.05,
) -> float:
    emotion = float(reinforcement.get("emotion", 0.0))
    outcome = float(reinforcement.get("outcome", 0.0))
    reuse = float(reinforcement.get("reuse", 0.0))
    delta = compute_importance(emotion, outcome, reuse, alpha, beta, gamma, clip=False)
    new_score = current_importance + delta + boost
    return max(0.0, min(1.0, new_score))