import { NavLink } from "react-router";
import { motion } from "framer-motion";
import {
  Home,
  Search,
  Clock,
  Database,
  Brain,
  Zap,
  BookOpen,
  Timer,
  Settings
} from "lucide-react";

const navItems = [
  { path: "/", label: "Dashboard", icon: Home },
  { path: "/search", label: "Search", icon: Search },
  { path: "/timeline", label: "Timeline", icon: Clock },
  { path: "/reasoning", label: "Reasoning", icon: Brain },
  { path: "/skills", label: "Skills", icon: Zap },
  { path: "/episodic", label: "Episodic", icon: BookOpen },
  { path: "/short-term", label: "Short-Term", icon: Timer },
  { path: "/management", label: "Management", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="w-56 border-r flex flex-col" style={{
      background: '#121821',
      borderColor: '#30363D'
    }}>
      <div className="p-6 border-b" style={{ borderColor: '#30363D' }}>
        <motion.h1
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xl tracking-wider"
          style={{ color: '#4F8CFF' }}
        >
          AION
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-xs mt-1"
          style={{ color: '#64748B' }}
        >
          Autonomous Intelligence Orchestrator
        </motion.p>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all text-sm ${
                isActive
                  ? 'bg-[#18212C] text-[#4F8CFF]'
                  : 'text-[#94A3B8] hover:bg-[#18212C] hover:text-[#F8FAFC]'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t text-xs" style={{
        borderColor: '#30363D',
        color: '#64748B'
      }}>
        <div className="flex items-center justify-between mb-1">
          <span>System Status</span>
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [1, 0.7, 1],
            }}
            transition={{
              repeat: Infinity,
              duration: 2,
            }}
            className="w-2 h-2 rounded-full bg-[#22C55E]"
            style={{
              boxShadow: '0 0 10px rgba(34, 197, 94, 0.5)',
            }}
          />
        </div>
        <div>Active Agents: 4</div>
      </div>
    </aside>
  );
}
