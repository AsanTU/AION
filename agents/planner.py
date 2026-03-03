from agents.base import BaseAgent
from agents.schema import AgentOutput

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Planner")

    def act(self, input_data: dict) -> dict:
        user_goal = input_data.get("goal", "")
        steps = [step.strip() for step in user_goal.replace(',', ',').split(',') if step.strip()]
        proposal = " -> ".join(steps)
        risks = []
        confidence = 0.8

        explanation = f"Decomposed goal into steps: {steps}"

        self.state["explanation"] = explanation

        return AgentOutput(
            agent="Planner",
            goal=user_goal,
            proposal=proposal,
            risks=risks,
            confidence=confidence,
            next_required_agent="Critic",
            explanation=explanation
        ).__dict__