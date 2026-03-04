from agents.planner import PlannerAgent
from agents.critic import CriticAgent
from agents.research import ResearchAgent
from agents.executor import ExecutorAgent
from memory.core.schema import MemoryEntry
from memory.backends.vector_db import VectorDB
from transformers import AutoTokenizer, AutoModel
import torch
import time
import uuid

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

vector_db = VectorDB(dim=384) 

def embedding_function(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()

def generate_unique_id():
    return str[uuid.uuid4()]

def store_reasoning(agent_name, agent_output):
    output_text = agent_output.get("explanation", "")
    embedding = embedding_function(output_text)
    memory_entry = MemoryEntry(
        id=generate_unique_id(),
        content=output_text,
        embedding=embedding,
        type="reasoning",
        tags=["debate", "agent_reasoning", agent_name],
        importance=0.5,
        decay_rate=0.01,
        created_at=time.time(),
        last_accessed=time.time(),
    )
    vector_db.add(memory_entry)

def orchestration_loop(user_input: dict):
    planner = PlannerAgent()
    critic = CriticAgent()
    researcher = ResearchAgent()
    executor = ExecutorAgent(system_prompt="You are a precise executor. Always confirm the action.")

    planner_output = planner.act(user_input)
    store_reasoning("Planner", planner_output)

    critic_output = critic.act(planner_output)
    store_reasoning("Critic", critic_output)

    issues_found = bool(critic_output.get("risks"))
    if issues_found:
        revised_input = dict(user_input)
        revised_input["risks"] = critic_output["risks"]
        planner_output = planner.act(revised_input)
        store_reasoning("Planner", planner_output)

    research_output = researcher.act(planner_output)
    store_reasoning("Researcher", research_output)

    refined_input = dict(user_input)
    refined_input["proposal"] = planner_output["proposal"]
    refined_input["risks"] = research_output["risks"]
    final_plan = planner.act(refined_input)
    store_reasoning("Planner", final_plan)

    execution_result = executor.act(final_plan)
    store_reasoning("Executor", execution_result)

    return execution_result

if __name__ == "__main__":
    user_input = {"goal": "Learn Python, build a project, get feedback"}
    result = orchestration_loop(user_input)
    print(result)