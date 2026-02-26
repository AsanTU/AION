import streamlit as st
import time
import random
from memory.api import MemoryAPI

# Dummy backend for demo; replace with your real LTSMManager
class DummyEntry:
    def __init__(self, id, content, created_at, importance, decay_rate, tags, influences=None):
        self.id = id
        self.content = content
        self.created_at = created_at
        self.last_accessed = created_at + 1000
        self.importance = importance
        self.decay_rate = decay_rate
        self.tags = tags
        self.reinforcement_events = [
            {"timestamp": created_at + 500, "delta": 0.1},
            {"timestamp": created_at + 800, "delta": 0.2},
        ]
        self.influences = influences or []

class DummyLTSM:
    def __init__(self):
        now = time.time()
        self.db = type("DB", (), {})()
        self.db.entries = {
            "1": DummyEntry("1", "Decision on 2024-11-03 (failure)", now-10000, 0.8, 0.01, ["decision"], ["2", "3"]),
            "2": DummyEntry("2", "Skill gap in ML fundamentals", now-20000, 0.7, 0.02, ["skill"]),
            "3": DummyEntry("3", "Repeated stress patterns", now-30000, 0.6, 0.015, ["stress"]),
        }

api = MemoryAPI(DummyLTSM())

st.title("Memory Inspection UI")

# ...existing code...

# List all memories
memories = api.timeline()
memory_options = {f"{m['content']} ({int(m['created_at'])})": m['id'] for m in memories}
selected_label = st.selectbox("Select a memory to inspect:", list(memory_options.keys()))
selected_id = memory_options[selected_label]
memory = next(m for m in memories if m['id'] == selected_id)

# Show memory details
st.subheader("Memory Details")
st.write(f"**Content:** {memory['content']}")
st.write(f"**Tags:** {', '.join(memory['tags'])}")
st.write(f"**Created at:** {time.ctime(memory['created_at'])}")
st.write(f"**Importance:** {memory['importance']}")
st.write(f"**Decay rate:** {memory['decay_rate']}")

if st.button("Boost Memory"):
    memory_obj = api.ltsm.db.entries[selected_id]
    memory_obj.importance = min(memory_obj.importance + 0.1, 1.0)
    memory_obj.reinforcement_events.append({
        "tiimestamp": time.time(),
        "delta": 0.1
    })
    st.success("Memory boosted!")

if st.button("Evict Memory"):
    del api.ltsm.db.entries[selected_id]
    st.success("Memory evicted!")
    st.rerun()

# Show history and decay curve
history = api.get_memory_history(memory_id=selected_id)
if history:
    st.subheader("Decay Curve")
    import matplotlib.pyplot as plt
    curve = history["decay_curve"]
    xs = [c["timestamp"] for c in curve]
    ys = [c["score"] for c in curve]
    fig, ax = plt.subplots()
    ax.plot(xs, ys)
    ax.set_xlabel("Time")
    ax.set_ylabel("Effective Score")
    st.pyplot(fig)

    st.subheader("Reinforcement Events")
    for evt in history["reinforcement_events"]:
        ts = evt.get("timestamp")
        delta = evt.get("delta", "?")
        if ts is not None:
            st.write(f"At {time.ctime(evt['timestamp'])}: Δimportance {evt['delta']}")
        else:
            st.write(f"Δimportance {delta} (timestamp missing)")

# Show "why" chain
st.subheader("Why Chain (Influence Tree)")
def render_why_chain(chain, level=0):
    if not chain or "memory" not in chain:
        return
    st.write(" " * level + f"- {chain['memory']}")
    for inf in chain.get("influences", []):
        render_why_chain(inf, level+1)

why_chain = api.why_chain(memory_id=selected_id, depth=3)
render_why_chain(why_chain)
