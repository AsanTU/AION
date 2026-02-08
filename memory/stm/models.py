from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class STMEntry:
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    source: str
    priority: int