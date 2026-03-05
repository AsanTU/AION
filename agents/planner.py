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
        base_confidence = 0.8
        confidence = self.calibrated_confidence(base_confidence)

        if self.has_repeated_failure("No feedback step included."):
            if not any("feedback" in step.lower() for step in steps):
                steps.append("Get feedback")
                proposal = " -> ".join(steps)
                risks.append("Feedback step was missing in previous plans; added automatically.")

        explanation = f"Decomposed goal into steps: {steps}"

        self.state["explanation"] = explanation

        output = AgentOutput(
            agent="Planner",
            goal=user_goal,
            proposal=proposal,
            risks=risks,
            confidence=confidence,
            next_required_agent="Critic",
            explanation=explanation
        ).__dict__

        self.record_conversation(input_data, output)

        return output