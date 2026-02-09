from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime
@dataclass
class LTSMEntry:
    id: str
    vector: List[float]
    metadata: Dict[str, Any]
    created_at: float
    last_accessed: float
    decay_rate: float

@dataclass
class EpisodicMemoryEntry:
    situation: str
    decision: str
    outcome: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)

@dataclass
class SkillHistoryEntry:
    timestamp: str
    value: float

@dataclass
class SkillMemoryEntry:
    skill_name: str
    current_value: float
    history: List[SkillHistoryEntry] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)