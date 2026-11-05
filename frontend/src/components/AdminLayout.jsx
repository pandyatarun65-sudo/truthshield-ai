import { NavLink, Outlet, Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

const items = [["/admin", "Dashboard", true], ["/admin/users", "Users"], ["/admin/posts", "Posts"], ["/admin/reports", "Reports"],
  ["/admin/knowledge-base", "Knowledge Base"], ["/admin/analytics", "Analytics"], ["/admin/logs", "Logs"]];

export default function AdminLayout() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen md:flex">
      <aside className="bg-slate-900 p-4 text-slate-200 md:w-56 md:min-h-screen">
        <div className="mb-4 text-lg font-bold">🛡 Admin Panel</div>
        <p className="mb-4 text-xs text-slate-400">Signed in as {user.username} ({user.role})</p>
        <nav className="flex flex-wrap gap-1 md:flex-col" aria-label="Admin">
          {items.map(([to, label, end]) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => `rounded-lg px-3 py-2 text-sm ${isActive ? "bg-indigo-600 text-white" : "hover:bg-slate-800"}`}>{label}</NavLink>
          ))}
          <Link to="/feed" className="rounded-lg px-3 py-2 text-sm hover:bg-slate-800">← Back to app</Link>
        </nav>
      </aside>
      <main className="flex-1 p-4 md:p-8"><Outlet /></main>
    </div>
  );
}
