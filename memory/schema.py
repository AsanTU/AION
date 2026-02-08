from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class LTSMEntry:
    id: str
    vector: List[float]
    metadata: Dict[str, Any]
    created_at: float
    last_accessed: float
    decay_rate: float