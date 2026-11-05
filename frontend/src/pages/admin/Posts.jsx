import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, errMsg } from "../../api";
import AnalysisPanel from "../../components/AnalysisPanel";
import Spinner from "../../components/Spinner";
import StatusBadge from "../../components/StatusBadge";

const STATUSES = ["", "UNDER_REVIEW", "BLOCKED", "WARNING", "PUBLISHED", "REMOVED"];

export default function Posts() {
  const [status, setStatus] = useState("UNDER_REVIEW");
  const [q, setQ] = useState("");
  const [rows, setRows] = useState(null);
  const [open, setOpen] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(null);
  const load = () => { setRows(null); api.get("/admin/posts", { params: { status: status || undefined, q: q || undefined } }).then((r) => setRows(r.data)).catch((e) => setError(errMsg(e))); };
  useEffect(() => { load(); }, [status]); // eslint-disable-line

  const act = async (p, action) => {
    const note = prompt(`Optional note for the user (${action}):`) ?? "";
    setBusy(p.id); setError("");
    try { await api.put(`/admin/posts/${p.id}`, { action, note: note || null }); load(); }
    catch (e) { setError(errMsg(e)); } finally { setBusy(null); }
  };
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Post moderation</h1>
      <form className="flex flex-wrap gap-2" onSubmit={(e) => { e.preventDefault(); load(); }}>
        <select aria-label="Status" className="input w-auto" value={status} onChange={(e) => setStatus(e.target.value)}>{STATUSES.map((s) => <option key={s} value={s}>{s || "All statuses"}</option>)}</select>
        <input aria-label="Search" className="input max-w-xs" placeholder="Search text" value={q} onChange={(e) => setQ(e.target.value)} />
        <button className="btn-primary">Filter</button>
      </form>
      {error && <p role="alert" className="text-red-600">{error}</p>}
      {!rows ? <Spinner /> : rows.length === 0 ? <p className="text-slate-500">No posts in this state.</p> : rows.map((p) => (
        <div key={p.id} className="card space-y-2">
          <div className="flex flex-wrap items-center gap-2 text-sm"><b>#{p.id} @{p.author.username}</b><StatusBadge post={p} /><span className="text-slate-500">risk {p.risk_score} · {p.category}</span></div>
          <p className="whitespace-pre-wrap text-sm">{p.text}</p>
          <div className="flex flex-wrap gap-2">
            <button className="btn-secondary" onClick={() => setOpen(open === p.id ? null : p.id)}>{open === p.id ? "Hide" : "View"} AI analysis</button>
            <button className="btn-success" disabled={busy === p.id} onClick={() => act(p, "approve")}>Approve</button>
            <button className="btn-danger" disabled={busy === p.id} onClick={() => act(p, "block")}>Block</button>
            {["BLOCKED", "REMOVED"].includes(p.status) && <button className="btn-secondary" disabled={busy === p.id} onClick={() => act(p, "restore")}>Restore</button>}
            {p.status !== "REMOVED" && <button className="btn-secondary" disabled={busy === p.id} onClick={() => act(p, "remove")}>Remove</button>}
            <Link className="btn-secondary" to={`/post/${p.id}`}>Open</Link>
          </div>
          {open === p.id && <div className="rounded-lg border p-3"><AnalysisPanel analysis={p.analysis} riskLevel={p.risk_level} /></div>}
        </div>
      ))}
    </div>
  );
}
