from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class AgentMessage:
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    memory_refs: List[str] = field(default_factory=list)