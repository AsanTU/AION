from datetime import datetime
from typing import Dict
import uuid

from memory.core.schema import MemoryEntry
from memory.api import _deterministic_embed
from memory.storage.sqlite_storage import load_memories, add_memory, delete_memory

class SkillMemory:
    def __init__(self):
        self.skills: Dict[str, MemoryEntry] = {
            entry.content: entry
            for entry in load_memories()
            if getattr(entry, "type", None) == "skill"
        }

    def add_or_update_skill(self, skill_name, value, tags=None, dim: int = 8):
        now = datetime.now().isoformat()
        if skill_name in self.skills:
            entry = self.skills[skill_name]
            entry.current_value = value
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
                metadata=metadata,
                public_memories = [m for m in self.ltsm.db.entries.values() if m.visibility == "public"]
            )
            entry.skill_name = skill_name
            entry.current_value = value
            entry.history = history
            self.skills[skill_name] = entry
            add_memory(entry)
        
    def delete_skill(self, skill_name):
        entry = self.skills.get(skill_name)
        if entry:
            delete_memory(entry.id)
            del self.skills[skill_name]

    def get_skill(self, skill_name):
        return self.skills.get(skill_name)

    def get_all_skills(self):
        return list(self.skills.values())