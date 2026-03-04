from agents.base import BaseAgent
from agents.schema import AgentOutput

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research")

    def act(self, input_data: dict) -> dict:
        goal = input_data.get("goal", "")
        proposal = input_data.get("proposal", "")
        risks = input_data.get("risks", [])
        info_gaps = []

        if "project" in proposal.lower() and "example" not in proposal.lower():
            info_gaps.append("No example project provided.")
        if "feedback" in proposal.lower() and "source" not in proposal.lower():
            info_gaps.append("No feedback source specified.")

        evidence = [
            "Python is widely used for beginner projects. [sorce: python.arg]",
            "Peer feedback accelerates learning. [source: educational research]"
        ]

        explanation = (
            f"Identified information gaps: {info_gaps}. "
            f"Provided evidence: {evidence}"
        )

        self.state["explanation"] = explanation

        output = AgentOutput(
            agent="Research",
            goal=goal,
            proposal=proposal,
            risks=risks + info_gaps,
            confidence=0.75,
            next_required_agent="Planner",
            explanation=explanation
        ).__dict__

        self.record_conversation(input_data, output)

        return output