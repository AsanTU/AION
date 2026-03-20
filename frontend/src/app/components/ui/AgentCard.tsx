import { motion } from "framer-motion";
import { Circle } from "lucide-react";

interface AgentCardProps {
  name: string;
  type: 'planner' | 'critic' | 'researcher' | 'executor';
  status: 'active' | 'idle' | 'thinking';
  confidence: number;
  reasoning?: string;
}

const agentColors = {
  planner: '#4F8CFF',
  critic: '#EF4444',
  researcher: '#A855F7',
  executor: '#22C55E',
};

export default function AgentCard({ name, type, status, confidence, reasoning }: AgentCardProps) {
  const color = agentColors[type];

  return (
    <motion.div
      className="p-4 rounded-xl border"
      style={{
        background: '#18212C',
        borderColor: status === 'active' ? color : '#30363D',
      }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <motion.div
            animate={status === 'active' ? {
              scale: [1, 1.2, 1],
              opacity: [1, 0.7, 1],
            } : {}}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <Circle className="w-3 h-3" fill={color} stroke={color} />
          </motion.div>
          <div>
            <h4 className="text-sm" style={{ color: '#F8FAFC' }}>
              {name}
            </h4>
            <p className="text-xs" style={{ color: color }}>
              {type}
            </p>
          </div>
        </div>
        <span className="text-xs px-2 py-1 rounded" style={{
          background: '#121821',
          color: status === 'active' ? '#22C55E' : '#64748B'
        }}>
          {status}
        </span>
      </div>

      {reasoning && (
        <p className="text-xs mb-3" style={{ color: '#94A3B8' }}>
          {reasoning}
        </p>
      )}

      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs" style={{ color: '#64748B' }}>
            Confidence
          </span>
          <span className="text-xs" style={{ color: '#F8FAFC' }}>
            {(confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="h-1 rounded-full overflow-hidden" style={{ background: '#121821' }}>
          <div
            className="h-full rounded-full"
            style={{
              width: `${confidence * 100}%`,
              background: color,
            }}
          />
        </div>
      </div>
    </motion.div>
  );
}
