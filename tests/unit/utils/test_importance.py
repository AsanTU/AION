import unittest
from datetime import datetime, timedelta, timezone
from math import isclose
from memory.utils.importance import compute_importance, effective_score, reinforce_importance
import math

class TestImportance(unittest.TestCase):
    def test_compute_importance_basic(self):
        imp = compute_importance(emotion=0.8, outcome=0.5, reuse=0.2, alpha=0.5, beta=0.3, gamma=0.2)
        self.assertAlmostEqual(imp, 0.59, places=6)
    
    def test_compute_importance_clipping(self):
        imp = compute_importance(1.0, 1.0, 1.0, alpha=1.0, beta=1.0, gamma=1.0)
        self.assertEqual(imp, 1.0)
    
    def test_effective_score_decay(self):
        importance = 1.0
        decay_rate = 0.1  
        then = datetime.now(timezone.utc) - timedelta(minutes=10)
        eff = effective_score(importance, decay_rate, timestamp=then.isoformat())
        dt_minutes = 10
        expected = 1.0 * math.exp(-0.1 * dt_minutes)
        self.assertTrue(isclose(eff, expected, rel_tol=1e-6))
    
    def test_reinforce_importance_increases(self):
        base = 0.2
        new = reinforce_importance(base, {"emotion":0.5, "outcome":0.2, "reuse":0.1}, boost=0.01)
        self.assertGreater(new, base)

if __name__ == "__main__":
    unittest.main()