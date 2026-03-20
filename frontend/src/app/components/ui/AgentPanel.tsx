import AgentCard from "./AgentCard.tsx";

const agents = [
  {
    name: "Alpha Planner",
    type: "planner" as const,
    status: "active" as const,
    confidence: 0.94,
    reasoning: "Analyzing task breakdown for memory search optimization",
  },
  {
    name: "Beta Critic",
    type: "critic" as const,
    status: "idle" as const,
    confidence: 0.87,
  },
  {
    name: "Gamma Researcher",
    type: "researcher" as const,
    status: "thinking" as const,
    confidence: 0.91,
    reasoning: "Gathering context from knowledge base",
  },
  {
    name: "Delta Executor",
    type: "executor" as const,
    status: "active" as const,
    confidence: 0.89,
    reasoning: "Implementing memory retrieval pipeline",
  },
];

export default function AgentPanel() {
  return (
    <div>
      <h2 className="text-lg mb-4" style={{ color: '#F8FAFC' }}>
        Active Agents
      </h2>
      <div className="grid grid-cols-2 gap-3">
        {agents.map((agent) => (
          <AgentCard key={agent.name} {...agent} />
        ))}
      </div>
    </div>
  );
}
