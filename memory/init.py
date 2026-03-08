"""
Memory package initialization.
Exports MemoryEntry and key API functions.
"""

__all__ = ["MemoryEntry", "write_memory", "__version__"]
__version__ = "0.0.0"

from .core.schema import MemoryEntry
from .api import write_memory