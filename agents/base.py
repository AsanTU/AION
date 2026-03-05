from agents.metrics import conn
import time

class BaseAgent:
    def __init__(self, name):
        self.name = name
        self.state = {
            "performance_scores": [],
            "failures": [],
            "confidence_history": [],
        }
        self.conversation_history = []
        self.debate_outcomes = []
        self.execution_results = []
        self.load_past_metrics()

    def load_past_metrics(self):
        cursor = conn.execute(
            "SELECT performance_score, failure_reason, confidence FROM agent_metrics WHERE agent_name=?",
            (self.name,)
        )
        for score, failure, confidence in cursor.fetchall():
            if score is not None:
                self.state["performance_scores"].append(score)
            if failure:
                self.state["failures"].append(failure)
            if confidence is not None:
                self.state["confidence_history"].append(confidence)

    def act(self, input_data: dict) -> dict:
        raise NotImplementedError
    
    def explain(self) -> str:
        return self.state.get("explanaiton", "")
    
    def record_conversation(self, input_data: dict, output: dict):
        self.conversation_history.append({"input": input_data, "output": output})

    def save_metrics(self, score, failure, confidence):
        conn.execute(
            'INSERT INTO agent_metrics (agent_name, timestamp, performance_score, failure_reason, confidence) VALUES (?, ?, ?, ?, ?)',
            (self.name, time.time(), score, failure, confidence)
        )
        conn.commit()

    def calibrated_confidence(self, base_confidence: float) -> float:
        if not self.state["performance_scores"]:
            return base_confidence
        avg_score = sum(self.state["performance_scores"]) / len(self.state["performance_scores"])
        return min(1.0, max(0.0, base_confidence * avg_score))

    def has_repeated_failure(self, failure_reason: str, threshold: int = 3) -> bool:
        return self.state["failures"].count(failure_reason) >= threshold