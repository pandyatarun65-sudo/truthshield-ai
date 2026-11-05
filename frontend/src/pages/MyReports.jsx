import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, errMsg } from "../api";
import Spinner from "../components/Spinner";

export default function MyReports() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { api.get("/reports").then((r) => setRows(r.data)).catch((e) => setError(errMsg(e))); }, []);
  if (error) return <p role="alert" className="text-red-600">{error}</p>;
  if (!rows) return <Spinner />;
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-bold">My report history</h1>
      {rows.length === 0 && <p className="text-slate-500">You have not reported any posts.</p>}
      {rows.map((r) => (
        <div key={r.report_id} className="card text-sm">
          <div className="flex justify-between"><b>#{r.report_id} · {r.reason}</b><span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold">{r.status}</span></div>
          <p className="mt-1 text-slate-600">“{r.post_text}”</p>
          {r.resolution_note && <p className="mt-1 text-slate-500">Moderator note: {r.resolution_note}</p>}
          <Link className="text-indigo-700 underline" to={`/post/${r.post_id}`}>View post</Link>
        </div>
      ))}
    </div>
  );
}
