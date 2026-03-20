import { createBrowserRouter } from "react-router";
import Root from "./components/Root.tsx";
import MemoryDashboard from "./components/screens/MemoryDashboard";
// import MemorySearch from "./components/screens/MemorySearch";
// import MemoryTimeline from "./components/screens/MemoryTimeline";
// import MemoryDetail from "./components/screens/MemoryDetail";
// import ReasoningViewer from "./components/screens/ReasoningViewer";
// import SkillsMemory from "./components/screens/SkillsMemory";
// import EpisodicMemory from "./components/screens/EpisodicMemory";
// import ShortTermMemory from "./components/screens/ShortTermMemory";
// import MemoryManagement from "./components/screens/MemoryManagement";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: MemoryDashboard },
    //   { path: "search", Component: MemorySearch },
    //   { path: "timeline", Component: MemoryTimeline },
    //   { path: "memory/:id", Component: MemoryDetail },
    //   { path: "reasoning", Component: ReasoningViewer },
    //   { path: "skills", Component: SkillsMemory },
    //   { path: "episodic", Component: EpisodicMemory },
    //   { path: "short-term", Component: ShortTermMemory },
    //   { path: "management", Component: MemoryManagement },
    ],
  },
]);
