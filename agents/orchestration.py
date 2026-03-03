from agents.planner import PlannerAgent
from agents.critic import CriticAgent
from agents.research import ResearchAgent
from agents.executor import ExecutorAgent

def orchestration_loop(user_input: dict):
    planner = PlannerAgent()
    critic = CriticAgent()
    researcher = ResearchAgent()
    executor = ExecutorAgent(system_prompt="You are a precise executor. Always confirm the action.")

    planner_output = planner.act(user_input)

    critic_output = critic.act(planner_output)

    issues_found = bool(critic_output.get("risks"))
    if issues_found:
        revised_input = dict(user_input)
        revised_input["risks"] = critic_output["risks"]
        planner_output = planner.act(revised_input)

    research_output = researcher.act(planner_output)

    refined_input = dict(user_input)
    refined_input["proposal"] = planner_output["proposal"]
    refined_input["risks"] = research_output["risks"]
    final_plan = planner.act(refined_input)

    execution_result = executor.act(final_plan)

    return execution_result

if __name__ == "__main__":
    user_input = {"goal": "Learn Python, build a project, get feedback"}
    result = orchestration_loop(user_input)
    print(result)