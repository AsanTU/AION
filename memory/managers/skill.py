from typing import Dict, List, Optional, Any
import uuid
import time

from memory.core.schema import MemoryEntry
from memory.api import _deterministic_embed
from memory.storage.sqlite_storage import load_memories, add_memory, delete_memory

class SkillMemory:
    """
    Manages skill memories: tracks skill values and their history.
    """
    def __init__(self):
        self.skills: Dict[str, MemoryEntry] = {
            entry.content: entry
            for entry in load_memories()
            if getattr(entry, "type", None) == "skill"
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
        if skill_name in self.skills:
            entry = self.skills[skill_name]
            entry.metadata.setdefault("history", []).append({"timestamp": now, "value": value})
            entry.metadata["current_value"] = value
            if tags:
                entry.tags = list(dict.fromkeys(entry.tags + tags))
                entry.metadata["tags"] = entry.tags
            add_memory(entry)
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
            add_memory(entry)
        return self.skills[skill_name]

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