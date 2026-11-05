import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, errMsg } from "../../api";
import Spinner from "../../components/Spinner";

export default function Reports() {
  const [status, setStatus] = useState("");
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(null);
  const load = () => { setRows(null); api.get("/admin/reports", { params: { status: status || undefined } }).then((r) => setRows(r.data)).catch((e) => setError(errMsg(e))); };
  useEffect(() => { load(); }, [status]); // eslint-disable-line

  const set = async (r, newStatus) => {
    const note = ["RESOLVED", "REJECTED"].includes(newStatus) ? prompt("Resolution note (optional):") ?? "" : "";
    setBusy(r.report_id); setError("");
    try { await api.put(`/admin/reports/${r.report_id}`, { status: newStatus, resolution_note: note || null }); load(); }
    catch (e) { setError(errMsg(e)); } finally { setBusy(null); }
  };
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Reports</h1>
      <select aria-label="Status filter" className="input w-auto" value={status} onChange={(e) => setStatus(e.target.value)}>
        {["", "PENDING", "UNDER_REVIEW", "RESOLVED", "REJECTED"].map((s) => <option key={s} value={s}>{s || "All"}</option>)}</select>
      {error && <p role="alert" className="text-red-600">{error}</p>}
      {!rows ? <Spinner /> : rows.length === 0 ? <p className="text-slate-500">No reports.</p> : rows.map((r) => (
        <div key={r.report_id} className="card space-y-2 text-sm">
          <div className="flex justify-between"><b>#{r.report_id} · {r.reason}</b><span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold">{r.status}</span></div>
          <p>Reported by <b>@{r.reporter}</b> · post #{r.post_id} ({r.post_status})</p>
          <p className="text-slate-600">“{r.post_text}”</p>
          {r.description && <p className="text-slate-500">Reporter says: {r.description}</p>}
          <div className="flex flex-wrap gap-2">
            <Link className="btn-secondary" to={`/post/${r.post_id}`}>View post & AI analysis</Link>
            {r.status === "PENDING" && <button className="btn-secondary" disabled={busy === r.report_id} onClick={() => set(r, "UNDER_REVIEW")}>Review</button>}
            {["PENDING", "UNDER_REVIEW"].includes(r.status) && (<>
              <button className="btn-success" disabled={busy === r.report_id} onClick={() => set(r, "RESOLVED")}>Resolve</button>
              <button className="btn-danger" disabled={busy === r.report_id} onClick={() => set(r, "REJECTED")}>Reject</button></>)}
          </div>
        </div>
      ))}
    </div>
  );
}
