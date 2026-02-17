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

def effective_score(
        importance: float,
        decay_rate: float,
        timestamp: Union[str, float, int, None] = None,
        now_ts: Union[str, float, int, None] = None,
) -> float:
    now_s = _to_timestamp_secs(now_ts)
    then_s = _to_timestamp_secs(timestamp)
    age_minutes = max(0.0, (now_s - then_s) / 60.0)
    return float(importance) * math.exp(-float(decay_rate) * age_minutes)

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