import openai
from agents.base import BaseAgent
from agents.schema import AgentOutput

openai.api_key = "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"

def call_llm(prompt: str, input_text: str) -> str:
    full_prompt = f"{prompt}\n{input_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text}
        ],
        max_tokens=256,
        temperature=0.7
    )
    return response.choices[0].message["content"].strip()

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

        output = AgentOutput(
            agent="Executor",
            goal=goal,
            proposal=proposal,
            risks=input_data.get("risks", []),
            confidence=0.9,
            next_required_agent="",
            explanation=explanation
        ).__dict__

        self.record_conversation(input_data, output)

        return output