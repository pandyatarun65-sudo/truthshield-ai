import { useEffect, useState } from "react";
import { api, errMsg } from "../../api";
import Spinner from "../../components/Spinner";

const EMPTY = { claim: "", verified_fact: "", source: "", category: "Health", verification_status: "FALSE" };

export default function Knowledge() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [rows, setRows] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const load = () => api.get("/admin/knowledge-base", { params: { q: q || undefined, status: status || undefined, category: category || undefined } })
    .then((r) => setRows(r.data)).catch((e) => setError(errMsg(e)));
  useEffect(() => { load(); }, [status, category]); // eslint-disable-line
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault(); setBusy(true); setError("");
    try {
      if (editing) await api.put(`/admin/knowledge-base/${editing}`, form); else await api.post("/admin/knowledge-base", form);
      setForm(EMPTY); setEditing(null); await load();
    } catch (err) { setError(errMsg(err)); } finally { setBusy(false); }
  };
  const del = async (k) => {
    if (!confirm("Delete this knowledge record?")) return;
    try { await api.delete(`/admin/knowledge-base/${k.knowledge_id}`); load(); } catch (e) { setError(errMsg(e)); }
  };
  const edit = (k) => { setEditing(k.knowledge_id); setForm({ claim: k.claim, verified_fact: k.verified_fact, source: k.source, category: k.category, verification_status: k.verification_status }); window.scrollTo(0, 0); };
  const cats = [...new Set((rows || []).map((r) => r.category))];

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Knowledge Base</h1>
      <form onSubmit={save} className="card grid gap-3 md:grid-cols-2">
        <h2 className="font-semibold md:col-span-2">{editing ? `Edit record #${editing}` : "Add knowledge"}</h2>
        <div className="md:col-span-2"><label className="label" htmlFor="claim">Claim</label><input id="claim" required className="input" value={form.claim} onChange={set("claim")} /></div>
        <div className="md:col-span-2"><label className="label" htmlFor="fact">Verified fact</label><textarea id="fact" required rows={2} className="input" value={form.verified_fact} onChange={set("verified_fact")} /></div>
        <div><label className="label" htmlFor="src">Source</label><input id="src" required className="input" value={form.source} onChange={set("source")} /></div>
        <div><label className="label" htmlFor="cat">Category</label><input id="cat" required className="input" value={form.category} onChange={set("category")} /></div>
        <div><label className="label" htmlFor="st">Verdict</label><select id="st" className="input" value={form.verification_status} onChange={set("verification_status")}><option>TRUE</option><option>FALSE</option><option>MISLEADING</option></select></div>
        <div className="flex items-end gap-2"><button className="btn-primary" disabled={busy}>{busy ? "Saving..." : editing ? "Update" : "Add"}</button>
          {editing && <button type="button" className="btn-secondary" onClick={() => { setEditing(null); setForm(EMPTY); }}>Cancel</button>}</div>
      </form>
      {error && <p role="alert" className="text-red-600">{error}</p>}
      <form className="flex flex-wrap gap-2" onSubmit={(e) => { e.preventDefault(); load(); }}>
        <input aria-label="Search knowledge" className="input max-w-xs" placeholder="Search claims" value={q} onChange={(e) => setQ(e.target.value)} />
        <select aria-label="Verdict filter" className="input w-auto" value={status} onChange={(e) => setStatus(e.target.value)}><option value="">All verdicts</option><option>TRUE</option><option>FALSE</option><option>MISLEADING</option></select>
        <select aria-label="Category filter" className="input w-auto" value={category} onChange={(e) => setCategory(e.target.value)}><option value="">All categories</option>{cats.map((c) => <option key={c}>{c}</option>)}</select>
        <button className="btn-primary">Search</button>
      </form>
      {!rows ? <Spinner /> : rows.map((k) => (
        <div key={k.knowledge_id} className="card text-sm">
          <div className="flex flex-wrap items-center justify-between gap-2"><b>{k.claim}</b><span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold">{k.verification_status}</span></div>
          <p className="mt-1 text-slate-600">{k.verified_fact}</p>
          <p className="text-xs text-slate-500">Source: {k.source} · {k.category}</p>
          <div className="mt-2 flex gap-2"><button className="btn-secondary" onClick={() => edit(k)}>Edit</button><button className="btn-danger" onClick={() => del(k)}>Delete</button></div>
        </div>
      ))}
    </div>
  );
}
