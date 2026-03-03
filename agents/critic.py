from agents.base import BaseAgent
from agents.schema import AgentOutput

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__("Critic")
    
    def act(self, input_data: dict) -> dict:
        proposal = input_data.get("proposal", "")
        goal = input_data.get("goal", "")
        risks = input_data.get("risks", [])
        improvements = []
        found_risks = list(risks)

        if not proposal:
            improvements.append("No proposal provided.")
            found_risks.append("No plan to critique.")
        else:
            if "and" not in proposal and "->" not in proposal:
                improvements.append("Proposal may be too simple or missing steps.")
            if "feedback" not in proposal.lower():
                found_risks.append("No feedback step included.")
        
        if "build" in proposal and "learn" not in proposal:
            found_risks.append("Building before learning may be illogical.")
        
        explanation = (
            f"Checked proposal for logical flaws and missing risks. "
            f"Improvements: {improvements}, Risks: {found_risks}"
        )

        self.state["explanation"] = explanation

        return AgentOutput(
            agent="Critic",
            goal=goal,
            proposal=proposal,
            risks=found_risks,
            confidence=0.7,
            next_required_agent="Planner",
            explanation=explanation
        ).__dict__