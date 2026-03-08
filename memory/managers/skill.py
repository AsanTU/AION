from typing import Dict, List, Optional
import uuid
import time

from memory.core.schema import MemoryEntry
from memory.api import _deterministic_embed
from memory.utils.reader import get_memories_by_type
from memory.utils.writer import save_memory, delete_memory

class SkillMemory:
    """
    Manages skill memories: tracks skill values and their history.
    """
    def __init__(self):
        # Load only 'skill' type memories
        self.skills: Dict[str, MemoryEntry] = {
            entry.content: entry
            for entry in get_memories_by_type("skill")
        }

    def add_or_update_skill(
        self,
        skill_name: str,
        value: float,
        tags: Optional[List[str]] = None,
        dim: int = 8
    ) -> MemoryEntry:
        """
        Add a new skill or update an existing skill's value and history.
        """
        now = time.time()
        entry = self.skills.get(skill_name)
        if entry:
            entry.metadata.setdefault("history", []).append({"timestamp": now, "value": value})
            entry.metadata["current_value"] = value
            if tags:
                entry.tags = list(dict.fromkeys(entry.tags + tags))
                entry.metadata["tags"] = entry.tags
        else:
            entry_id = f"skill-{uuid.uuid4().hex}"
            history = [{"timestamp": now, "value": value}]
            embedding = _deterministic_embed(skill_name, dim=dim)
            metadata = {
                "skill_name": skill_name,
                "current_value": value,
                "history": history,
                "tags": tags or [],
            }
            entry = MemoryEntry(
                id=entry_id,
                content=skill_name,
                embedding=embedding,
                type="skill",
                tags=tags or [],
                importance=0.0,
                confidence=0.0,
                created_at=now,
                last_accessed=now,
                decay_rate=0.0,
                source="skill",
                linked_memories=[],
                metadata=metadata
            )
            self.skills[skill_name] = entry
        save_memory(entry)
        return entry

    def delete_skill(self, skill_name: str) -> None:
        """
        Delete a skill by name.
        """
        entry = self.skills.get(skill_name)
        if entry:
            delete_memory(entry.id)
            del self.skills[skill_name]

    def get_skill(self, skill_name: str) -> Optional[MemoryEntry]:
        """
        Get a skill entry by name.
        """
        return self.skills.get(skill_name)

    def get_all_skills(self) -> List[MemoryEntry]:
        """
        Get all skill entries.
        """
        return list(self.skills.values())