import unittest
from datetime import datetime, timedelta, timezone
from math import isclose, exp
from memory.utils.importance import compute_importance, effective_score, reinforce_importance, _to_timestamp_secs
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
        decay_rate = 0.1  # per minute
        then = datetime.now(timezone.utc) - timedelta(minutes=10)
        eff = effective_score(importance, decay_rate, timestamp=then.isoformat())
        dt_minutes = 10
        expected = 1.0 * exp(-0.1 * dt_minutes)
        self.assertTrue(isclose(eff, expected, rel_tol=1e-6))
    
    def test_reinforce_importance_increases(self):
        base = 0.2
        new = reinforce_importance(base, {"emotion":0.5, "outcome":0.2, "reuse":0.1}, boost=0.01)
        self.assertGreater(new, base)

    def test__to_timestamp_secs(self):
        # None returns current time (allow some slack)
        now = _to_timestamp_secs(None)
        self.assertTrue(abs(now - _to_timestamp_secs(None)) < 2)

        # Float and int
        self.assertEqual(_to_timestamp_secs(12345.6), 12345.6)
        self.assertEqual(_to_timestamp_secs(12345), 12345.0)

        # Datetime
        dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(_to_timestamp_secs(dt), dt.timestamp())

        # ISO string
        iso = "2020-01-01T00:00:00+00:00"
        self.assertEqual(_to_timestamp_secs(iso), dt.timestamp())

        # String float
        self.assertEqual(_to_timestamp_secs("12345.6"), 12345.6)

        # Bad string returns current time (allow some slack)
        t = _to_timestamp_secs("not-a-date")
        self.assertTrue(abs(t - _to_timestamp_secs(None)) < 2)

if __name__ == "__main__":
    unittest.main()