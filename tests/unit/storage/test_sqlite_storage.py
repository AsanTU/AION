import os
import tempfile
import unittest
from cryptography.fernet import Fernet
from memory.core.schema import MemoryEntry

# Patch the key and db location for testing
import memory.storage.sqlite_storage as storage

class TestSQLiteStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temp key and db
        cls.key_file = tempfile.NamedTemporaryFile(delete=False)
        cls.key_file.write(Fernet.generate_key())
        cls.key_file.close()
        cls.db_file = tempfile.NamedTemporaryFile(delete=False)
        cls.db_file.close()
        # Patch the functions to use temp files
        storage.get_cipher = lambda: Fernet(open(cls.key_file.name, "rb").read())
        storage.get_connection = lambda: storage.sqlite3.connect(cls.db_file.name)
        storage.init_db()

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.key_file.name)
        os.unlink(cls.db_file.name)

    def test_add_and_load_memory(self):
        entry = MemoryEntry(
            id="test1",
            content="test content",
            embedding=[0.1, 0.2, 0.3],
            type="test",
            tags=["a", "b"],
            importance=0.5,
            confidence=0.8,
            created_at=123.0,
            last_accessed=123.0,
            decay_rate=0.01,
            source="unit",
            linked_memories=[],
            metadata={"foo": "bar"}
        )
        storage.add_memory(entry)
        loaded = storage.load_memories()
        self.assertTrue(any(e.id == "test1" and e.content == "test content" for e in loaded))

    def test_delete_memory(self):
        entry = MemoryEntry(
            id="test2",
            content="to delete",
            embedding=[0.1, 0.2, 0.3],
            type="test",
            tags=["x"],
            importance=0.1,
            confidence=0.1,
            created_at=1.0,
            last_accessed=1.0,
            decay_rate=0.01,
            source="unit",
            linked_memories=[],
            metadata={}
        )
        storage.add_memory(entry)
        storage.delete_memory("test2")
        loaded = storage.load_memories()
        self.assertFalse(any(e.id == "test2" for e in loaded))

    def test_init_db_idempotent(self):
        # Should not raise even if called again
        try:
            storage.init_db()
        except Exception as e:
            self.fail(f"init_db raised {e}")

if __name__ == "__main__":
    unittest.main()