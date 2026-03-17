def print_reasoning_memories(memories, decision: str):
    """
    Print the decision and the reasoning memories in a readable CLI format.
    """
    print(f"\nDecision: {decision}\n")
    print("Reasoning memories:")
    for i, mem in enumerate(memories, 1):
        # Support both dict and MemoryEntry
        content = getattr(mem, "content", None) or mem.get("content")
        tags = getattr(mem, "tags", None) or mem.get("tags") or mem.get("metadata", {}).get("tags", [])
        importance = getattr(mem, "importance", None) or mem.get("importance") or mem.get("metadata", {}).get("importance", 0.0)
        print(f"{i}. {content} (tags: {tags}, importance: {importance:.2f})")