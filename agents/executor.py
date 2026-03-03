from agents.base import BaseAgent
from agents.schema import AgentOutput

def call_llm(prompt: str, input_text: str) -> str:
    # Replace this with your actual LLM API call
    return f"Executed: {input_text} (Prompt: {prompt})"

class ExecutorAgent(BaseAgent):
    def __init__(self, system_prompt="You are an executor agent."):
        super().__init__("Executor")
        self.system_prompt = system_prompt

    def act(self, input_data: dict) -> dict:
        goal = input_data.get("goal", "")
        proposal = input_data.get("proposal", "")
        prompt = f"{self.system_prompt}\nGoal: {goal}\nAction: {proposal}\n"
        result = call_llm(prompt, proposal)
        explanation = f"Executed proposal using LLM backend. Result: {result}"

        self.state["explanation"] = explanation

        return AgentOutput(
            agent="Executor",
            goal=goal,
            proposal=proposal,
            risks=input_data.get("risks", []),
            confidence=0.9,
            next_required_agent="",
            explanation=explanation
        ).__dict__