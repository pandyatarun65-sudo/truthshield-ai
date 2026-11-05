import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../AuthContext";

const link = ({ isActive }) => `rounded-lg px-3 py-2 text-sm font-medium ${isActive ? "bg-indigo-100 text-indigo-700" : "text-slate-600 hover:bg-slate-100"}`;

export default function Layout() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    api.get("/notifications").then((r) => setUnread(r.data.unread)).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b bg-white">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-2 px-4 py-2">
          <Link to="/" className="mr-4 text-lg font-bold text-indigo-700">🛡 TruthShield AI</Link>
          <nav className="flex flex-wrap items-center gap-1" aria-label="Main">
            <NavLink to="/" end className={link}>Home</NavLink>
            <NavLink to="/explore" className={link}>Explore</NavLink>
            <NavLink to="/create-post" className={link}>Create Post</NavLink>
            <NavLink to="/notifications" className={link}>Notifications{unread > 0 && <span className="ml-1 rounded-full bg-red-600 px-1.5 text-xs text-white">{unread}</span>}</NavLink>
            <NavLink to="/profile" className={link}>Profile</NavLink>
            {["admin", "moderator"].includes(user.role) && <NavLink to="/admin" className={link}>Admin</NavLink>}
          </nav>
          <button className="btn-secondary ml-auto" onClick={() => { logout(); nav("/login"); }}>Logout</button>
        </div>
      </header>
      <main className="mx-auto max-w-3xl px-4 py-6"><Outlet /></main>
    </div>
  );
}
