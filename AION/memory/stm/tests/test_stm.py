import unittest
import time
from datetime import datetime, timedelta

from stm.stm import ShortTermMemory

class TestShortTermMemory(unittest.TestCase):
    def test_expiration(self):
        stm = ShortTermMemory(eviction_interval=1)
        stm.set("foo", "bar", ttl_minutes=0.001)
        time.sleep(0.1)
        self.assertIsNone(stm.get("foo"))
        stm.stop_eviction()

    def test_overwrite(self):
        stm = ShortTermMemory()
        stm.set("key", "value1", ttl_minutes=1)
        stm.set("key", "value2", ttl_minutes=1)
        self.assertEqual(stm.get("key"), "value2")
        stm.stop_eviction()

if __name__ == "__main__":
    unittest.main()