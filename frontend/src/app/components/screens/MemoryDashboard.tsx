import { Database, TrendingUp, Clock, AlertTriangle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import StatCard from "../ui/StatCard.tsx";
import MemoryCard from "../ui/MemoryCard.tsx";
import TimelineItem from "../ui/TimelineItem.tsx";
import AgentPanel from "../ui/AgentPanel.tsx";
import { motion } from "framer-motion";

const recentMemories = [
  {
    id: 1,
    content: "User prefers dark mode interfaces with high contrast",
    type: "semantic",
    importance: 0.89,
    timestamp: "2 hours ago",
    tags: ["preference", "ui"],
  },
  {
    id: 2,
    content: "Successfully implemented authentication flow using JWT",
    type: "episodic",
    importance: 0.76,
    timestamp: "5 hours ago",
    tags: ["achievement", "auth"],
  },
  {
    id: 3,
    content: "Database query optimization reduced latency by 40%",
    type: "procedural",
    importance: 0.92,
    timestamp: "1 day ago",
    tags: ["optimization", "database"],
  },
];

export default function MemoryDashboard() {
  const navigate = useNavigate();

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl mb-2" style={{ color: '#F8FAFC' }}>
          Memory Dashboard
        </h1>
        <p className="text-sm" style={{ color: '#64748B' }}>
          System-wide memory analytics and recent activity
        </p>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total Memories"
          value="2,847"
          icon={Database}
          color="#4F8CFF"
          trend="+12% this week"
        />
        <StatCard
          label="Avg Importance"
          value="0.78"
          icon={TrendingUp}
          color="#1CE6C9"
          trend="Stable"
        />
        <StatCard
          label="Active Memories"
          value="342"
          icon={Clock}
          color="#22C55E"
          trend="+5 today"
        />
        <StatCard
          label="Decaying Soon"
          value="23"
          icon={AlertTriangle}
          color="#F59E0B"
          trend="Review needed"
        />
      </div>

      <div className="mb-8">
        <AgentPanel />
      </div>

      <div className="grid grid-cols-3 gap-8">
        <div className="col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg" style={{ color: '#F8FAFC' }}>
              Recent Timeline
            </h2>
            <button
              onClick={() => navigate('/timeline')}
              className="text-xs px-3 py-1.5 rounded-lg hover:opacity-70 transition-opacity"
              style={{
                background: '#18212C',
                color: '#4F8CFF',
                border: '1px solid #30363D',
              }}
            >
              View All
            </button>
          </div>
          <div className="rounded-xl border p-6" style={{
            background: '#18212C',
            borderColor: '#30363D',
          }}>
            {recentMemories.map((memory) => (
              <TimelineItem key={memory.id} {...memory} />
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-lg mb-4" style={{ color: '#F8FAFC' }}>
            Metrics
          </h2>
          <div className="space-y-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="rounded-xl border p-4"
              style={{
                background: '#18212C',
                borderColor: '#30363D',
              }}
            >
              <h3 className="text-sm mb-3" style={{ color: '#F8FAFC' }}>
                Memory Distribution
              </h3>
              <div className="space-y-3">
                {[
                  { label: 'Episodic', value: 42, color: '#4F8CFF' },
                  { label: 'Semantic', value: 35, color: '#1CE6C9' },
                  { label: 'Procedural', value: 18, color: '#A855F7' },
                  { label: 'Skills', value: 5, color: '#22C55E' },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs" style={{ color: '#94A3B8' }}>
                        {item.label}
                      </span>
                      <span className="text-xs" style={{ color: '#F8FAFC' }}>
                        {item.value}%
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full overflow-hidden" style={{ background: '#121821' }}>
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${item.value}%`,
                          background: item.color,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="rounded-xl border p-4"
              style={{
                background: '#18212C',
                borderColor: '#30363D',
              }}
            >
              <h3 className="text-sm mb-3" style={{ color: '#F8FAFC' }}>
                Confidence Average
              </h3>
              <div className="text-3xl mb-2" style={{ color: '#22C55E' }}>
                87%
              </div>
              <p className="text-xs" style={{ color: '#64748B' }}>
                Across all active memories
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
