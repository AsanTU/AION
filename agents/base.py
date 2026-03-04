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