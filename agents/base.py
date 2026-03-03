class BaseAgent:
    def __init__(self, name):
        self.name = name
        self.state = {}

    def act(self, input_data: dict) -> dict:
        raise NotImplementedError
    
    def explain(self) -> str:
        return self.state.get("explanaiton", "")