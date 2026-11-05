import { useEffect, useState } from "react";
import { api, errMsg } from "../../api";
import { useAuth } from "../../AuthContext";
import Spinner from "../../components/Spinner";

export default function Users() {
  const { user: me } = useAuth();
  const [q, setQ] = useState("");
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);
  const load = () => api.get("/admin/users", { params: { q: q || undefined } }).then((r) => setRows(r.data)).catch((e) => setError(errMsg(e)));
  useEffect(() => { load(); }, []); // eslint-disable-line

  const toggle = async (u) => {
    setBusyId(u.id); setError("");
    try { await api.put(`/admin/users/${u.id}`, { is_active: !u.is_active }); await load(); }
    catch (e) { setError(errMsg(e)); } finally { setBusyId(null); }
  };
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Users</h1>
      <form className="flex gap-2" onSubmit={(e) => { e.preventDefault(); load(); }}>
        <input aria-label="Search users" className="input max-w-sm" placeholder="Search username or email" value={q} onChange={(e) => setQ(e.target.value)} />
        <button className="btn-primary">Search</button>
      </form>
      {error && <p role="alert" className="text-red-600">{error}</p>}
      {!rows ? <Spinner /> : (
        <div className="card overflow-x-auto p-0"><table className="w-full text-left text-sm">
          <thead className="bg-slate-100 text-xs uppercase text-slate-500"><tr><th className="p-3">User</th><th>Role</th><th>Trust</th><th>Posts</th><th>Reports</th><th>Status</th><th></th></tr></thead>
          <tbody>{rows.map((u) => (
            <tr key={u.id} className="border-t"><td className="p-3"><b>{u.username}</b><br /><span className="text-xs text-slate-500">{u.email}</span></td>
              <td>{u.role}</td><td>{u.trust_score}</td><td>{u.post_count}</td><td>{u.report_count}</td>
              <td>{u.is_active ? <span className="text-emerald-700">Active</span> : <span className="text-red-600">Suspended</span>}</td>
              <td className="pr-3 text-right">{me.role === "admin" && u.role !== "admin" &&
                <button className={u.is_active ? "btn-danger" : "btn-success"} disabled={busyId === u.id} onClick={() => toggle(u)}>{busyId === u.id ? "..." : u.is_active ? "Suspend" : "Activate"}</button>}</td></tr>
          ))}</tbody></table></div>
      )}
    </div>
  );
}
