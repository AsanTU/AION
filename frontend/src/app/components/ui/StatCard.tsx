import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color?: string;
  trend?: string;
}

export default function StatCard({
  label,
  value,
  icon: Icon,
  color = '#4F8CFF',
  trend
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="p-4 rounded-xl border"
      style={{
        background: '#18212C',
        borderColor: '#30363D',
      }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="p-2 rounded-lg" style={{ background: `${color}20` }}>
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
        {trend && (
          <span className="text-xs" style={{ color: '#64748B' }}>
            {trend}
          </span>
        )}
      </div>
      <div className="text-2xl mb-1" style={{ color: '#F8FAFC' }}>
        {value}
      </div>
      <div className="text-xs" style={{ color: '#64748B' }}>
        {label}
      </div>
    </motion.div>
  );
}
