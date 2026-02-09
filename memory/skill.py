from datetime import datetime
from typing import Dict

from memory.schema import SkillHistoryEntry, SkillMemoryEntry


class SkillMemory:
    def __init__(self):
        self.skills: Dict[str, SkillMemoryEntry] = {}

    def add_or_update_skill(self, skill_name, value, tags=None):
        now = datetime.now().isoformat()
        if skill_name in self.skills:
            entry = self.skills[skill_name]
            entry.current_value = value
            entry.history.append(SkillHistoryEntry(timestamp=now, value=value))
            if tags:
                entry.tags = list(set(entry.tags).union(tags))

        else:
            self.skills[skill_name] = SkillMemoryEntry(
                skill_name=skill_name,
                current_value=value,
                history=[SkillHistoryEntry(timestamp=now, value=value)],
                tags=tags or []
            )

    def get_skill(self, skill_name):
        return self.skills.get(skill_name)

    def get_all_skills(self):
        return list(self.skills.values())