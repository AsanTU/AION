import unittest

from memory.managers.skill import SkillMemory

class TestSkillMemory(unittest.TestCase):
    def test_add_and_update_skill(self):
        skm = SkillMemory()
        skm.add_or_update_skill("Python", 0.7, tags=["programming"])
        skm.add_or_update_skill("Python", 0.9)
        skill = skm.get_skill("Python")
        self.assertEqual(skill.metadata["skill_name"], "Python")
        self.assertEqual(skill.metadata["current_value"], 0.9)
        self.assertGreaterEqual(len(skill.metadata["history"]), 2)

    def test_tags(self):
        skm = SkillMemory()
        skm.add_or_update_skill("Math", 0.5, tags=["logic"])
        skm.add_or_update_skill("Math", 0.6, tags=["quantitative"])
        skill = skm.get_skill("Math")
        self.assertIn("logic", skill.tags)
        self.assertIn("quantitative", skill.tags)

    def test_delete_skill(self):
        skm = SkillMemory()
        skm.add_or_update_skill("DeleteMe", 0.5)
        self.assertIsNotNone(skm.get_skill("DeleteMe"))
        skm.delete_skill("DeleteMe")
        self.assertIsNone(skm.get_skill("DeleteMe"))

    def test_get_all_skills(self):
        skm = SkillMemory()
        skm.add_or_update_skill("SkillA", 0.1)
        skm.add_or_update_skill("SkillB", 0.2)
        all_skills = skm.get_all_skills()
        skill_names = [s.content for s in all_skills]
        self.assertIn("SkillA", skill_names)
        self.assertIn("SkillB", skill_names)

if __name__ == "__main__":
    unittest.main()