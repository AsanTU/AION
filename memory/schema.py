from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime

@dataclass
class MemoryEntry:
    id: str
    content: str
    embedding: List[float]
    type: str
    tags: List[str] = field(default_factory=list)
    importance: float = 0.0
    confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())
    decay_rate: float = 0.0
    source: str = "system"
    linked_memories: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)