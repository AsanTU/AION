import { motion } from "framer-motion";

interface TimelineItemProps {
  content: string;
  type: string;
  importance: number;
  timestamp: string;
  tags?: string[];
}

export default function TimelineItem({
  content,
  type,
  importance,
  timestamp,
  tags = []
}: TimelineItemProps) {
  const getTypeColor = (t: string) => {
    const colors: Record<string, string> = {
      episodic: '#4F8CFF',
      semantic: '#1CE6C9',
      procedural: '#A855F7',
      skill: '#22C55E',
    };
    return colors[t.toLowerCase()] || '#94A3B8';
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex gap-4 group"
    >
      <div className="flex flex-col items-center">
        <div
          className="w-3 h-3 rounded-full border-2"
          style={{
            borderColor: getTypeColor(type),
            background: '#18212C',
          }}
        />
        <div className="w-px flex-1 mt-2" style={{ background: '#30363D' }} />
      </div>

      <div className="flex-1 pb-6">
        <div className="flex items-center gap-2 mb-2">
          <span
            className="text-xs px-2 py-0.5 rounded"
            style={{
              background: `${getTypeColor(type)}20`,
              color: getTypeColor(type),
            }}
          >
            {type}
          </span>
          <span className="text-xs" style={{ color: '#64748B' }}>
            {timestamp}
          </span>
        </div>

        <p className="text-sm mb-2" style={{ color: '#F8FAFC' }}>
          {content}
        </p>

        <div className="flex items-center gap-3">
          <div className="flex-1">
            <div className="h-1 rounded-full overflow-hidden" style={{ background: '#121821' }}>
              <div
                className="h-full rounded-full"
                style={{
                  width: `${importance * 100}%`,
                  background: getTypeColor(type),
                }}
              />
            </div>
          </div>
          <span className="text-xs" style={{ color: '#64748B' }}>
            {(importance * 100).toFixed(0)}%
          </span>
        </div>

        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {tags.map((tag, i) => (
              <span
                key={i}
                className="text-xs px-2 py-0.5 rounded"
                style={{ background: '#121821', color: '#94A3B8' }}
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
