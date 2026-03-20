import { motion } from "framer-motion";
import { Tag as TagIcon } from "lucide-react";

interface MemoryCardProps {
  content: string;
  tags?: string[];
  importance: number;
  confidence: number;
  score?: number;
  timestamp?: string;
  type?: string;
  onClick?: () => void;
}

export default function MemoryCard({
  content,
  tags = [],
  importance,
  confidence,
  score,
  timestamp,
  type,
  onClick
}: MemoryCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      onClick={onClick}
      className={`p-4 rounded-xl border ${onClick ? 'cursor-pointer' : ''}`}
      style={{
        background: '#18212C',
        borderColor: '#30363D',
      }}
    >
      <div className="flex items-start justify-between gap-4 mb-3">
        <p className="flex-1 text-sm" style={{ color: '#F8FAFC' }}>
          {content}
        </p>
        {type && (
          <span
            className="text-xs px-2 py-1 rounded"
            style={{ background: '#121821', color: '#1CE6C9' }}
          >
            {type}
          </span>
        )}
      </div>

      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {tags.map((tag, i) => (
            <span
              key={i}
              className="text-xs px-2 py-1 rounded flex items-center gap-1"
              style={{ background: '#121821', color: '#94A3B8' }}
            >
              <TagIcon className="w-3 h-3" />
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs" style={{ color: '#64748B' }}>
              Importance
            </span>
            <span className="text-xs" style={{ color: '#F8FAFC' }}>
              {(importance * 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-1 rounded-full overflow-hidden" style={{ background: '#121821' }}>
            <div
              className="h-full rounded-full"
              style={{
                width: `${importance * 100}%`,
                background: `linear-gradient(90deg, #4F8CFF, #1CE6C9)`,
              }}
            />
          </div>
        </div>

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
                background: '#22C55E',
              }}
            />
          </div>
        </div>
      </div>

      {(score !== undefined || timestamp) && (
        <div className="flex items-center justify-between mt-3 pt-3 border-t" style={{ borderColor: '#30363D' }}>
          {score !== undefined && (
            <span className="text-xs" style={{ color: '#64748B' }}>
              Score: <span style={{ color: '#4F8CFF' }}>{score.toFixed(3)}</span>
            </span>
          )}
          {timestamp && (
            <span className="text-xs" style={{ color: '#64748B' }}>
              {timestamp}
            </span>
          )}
        </div>
      )}
    </motion.div>
  );
}
