__all__ = ["MemoryEntry", "__version__"]
__version__ = "0.0.0"

from .core.schema import MemoryEntry

def write_memory(*args, **kwargs):
    from .api import write_memory as _wm
    return _wm(*args, **kwargs)