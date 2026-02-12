import unittest

from memory.managers.skill import SkillMemory

class TestSkillMemory(unittest.TestCase):
    def test_add_and_update_skill(self):
        skm = SkillMemory()
        skm.add_or_update_skill("Python", 0.7, tags=["programming"])
        skm.add_or_update_skill("Python", 0.9)
        skill = skm.get_skill("Python")
        self.assertEqual(skill.skill_name, "Python")
        self.assertEqual(skill.current_value, 0.9)
        self.assertGreaterEqual(len(skill.history), 2)

    def test_tags(self):
        skm = SkillMemory()
        skm.add_or_update_skill("Math", 0.5, tags=["logic"])
        skm.add_or_update_skill("Math", 0.6, tags=["quantitative"])
        skill = skm.get_skill("Math")
        self.assertIn("logic", skill.tags)
        self.assertIn("quantitative", skill.tags)

if __name__ == "__main__":
    unittest.main()