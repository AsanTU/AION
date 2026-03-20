import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar.tsx";

export default function Root() {
  return (
    <div className="flex h-screen w-screen overflow-hidden" style={{ background: '#0B0F14' }}>
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
