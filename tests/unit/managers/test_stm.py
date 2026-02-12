import unittest
import time
import threading
from datetime import datetime, timedelta

from memory.managers.stm import ShortTermMemory

class NoEvictionSTM(ShortTermMemory):
    def __init__(self):
        self.store = {}
        self._lock = threading.Lock()

class TestShortTermMemory(unittest.TestCase):
    def test_expiration(self):
        stm = ShortTermMemory(eviction_interval=1)
        stm.set("foo", "bar", ttl_minutes=0.001)
        time.sleep(0.1)
        self.assertIsNone(stm.get("foo"))
        stm.stop_eviction()

    def test_overwrite(self):
        stm = ShortTermMemory(eviction_interval=10)
        stm.set("key", "value1", ttl_minutes=5)
        stm.set("key", "value2", ttl_minutes=5)
        self.assertEqual(stm.get("key"), "value2")
        stm.stop_eviction()

    def test_cleanup_manual(self):
        stm = ShortTermMemory(eviction_interval=100)
        stm.set("a", "b", ttl_minutes=0.001)
        time.sleep(0.1)
        stm.cleanup()
        self.assertIsNone(stm.get("a"))
        stm.stop_eviction()

    def test_priority_and_source(self):
        stm = ShortTermMemory()
        stm.set("p", "v", ttl_minutes=1, source="test", priority=10)
        entry = stm.store["p"]
        self.assertEqual(entry.source, "test")
        self.assertEqual(entry.metadata["priority"], 10)
        stm.stop_eviction()

    def test_thread_safety(self):
        stm = ShortTermMemory(start_eviction_thread=False)
        for i in range(100):
            stm.set(f"k{i}", f"v{i}", ttl_minutes=10)
        values = [stm.get(f"k{i}") for i in range(100)]
        self.assertEqual(values, [f"v{i}" for i in range(100)])

if __name__ == "__main__":
    unittest.main()