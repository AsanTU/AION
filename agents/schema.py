from dataclasses import dataclass, field
from typing import List

@dataclass
class AgentOutput:
    agent: str
    goal: str
    proposal: str
    risks: List[str] = field(default_factory=list)
    confidence: float = 0.0
    next_required_agent: str = ""
    explanation: str = ""