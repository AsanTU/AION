# AION Memory System

## Memory Types

AION supports multiple memory types, each designed for a specific aspect of agent cognition:

- **Episodic Memory:**  
  Stores sequences of events or experiences, allowing the agent to recall and reason about past situations.

- **Semantic Memory:**  
  Contains general knowledge, facts, and concepts learned by the agent.

- **Short-Term Memory (STM):**  
  Holds recent, high-priority information for immediate reasoning and context.

- **Skill Memory:**  
  Tracks learned skills, abilities, and their reinforcement over time.

Each memory entry includes metadata such as importance, decay rate, tags, timestamps, and visibility controls.

---

## Decay Math

AION uses exponential decay to model the fading of memory importance over time:

- **importance:** Initial significance of the memory (0.0–1.0).
- **decay_rate:** How quickly the memory fades (per minute).
- **Δt:** Time elapsed since last access or creation (in minutes).

Reinforcement events can increase importance, counteracting decay.

---

## Retrieval Logic

When an agent queries memory, AION retrieves and ranks memories using:

1. **Semantic Similarity:**  
   Finds memories most similar to the query using vector embeddings.

2. **Importance Weighting:**  
   Prioritizes memories with higher importance scores.

3. **Time Decay Adjustment:**  
   Adjusts scores based on how recently and frequently a memory was accessed.

4. **Type and Tag Filtering:**  
   Filters results by memory type or user-defined tags.

**Final Score Calculation:**
Only the top-K memories are injected into agent reasoning, with full explainability for each selection.

---

## Ethical Considerations

AION is designed with privacy, transparency, and user control as core principles:

- **Local-First Storage:**  
  All memory data is stored locally by default, ensuring user ownership.

- **Encryption at Rest:**  
  Memory data is encrypted on disk to protect against unauthorized access.

- **Explicit Deletion:**  
  Users can delete individual memories or all memories related to a topic (“Forget everything related to X”).

- **Visibility Controls:**  
  Memories can be marked as public, private, or hidden, giving users granular control over what is accessible.

- **Explainability:**  
  Every memory retrieval includes a transparent explanation of why it was selected, supporting auditability and trust.

- **No Cloud Sync by Default:**  
  Data is never uploaded or shared without explicit user consent.

**AION aims to set a new standard for ethical, user-centric memory systems in AI.**

---