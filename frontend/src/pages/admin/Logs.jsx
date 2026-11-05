import { useEffect, useState } from "react";
import { api, errMsg } from "../../api";
import Spinner from "../../components/Spinner";

const ACTIONS = ["", "LOGIN", "LOGIN_FAILED", "REGISTER", "POST_DECISION", "ADMIN_POST_ACTION", "REPORT_CREATED", "REPORT_ACTION", "USER_SUSPENDED", "USER_ACTIVATED", "KB_ADDED", "KB_EDITED", "KB_DELETED"];

export default function Logs() {
  const [action, setAction] = useState("");
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { setRows(null); api.get("/admin/logs", { params: { action: action || undefined } }).then((r) => setRows(r.data)).catch((e) => setError(errMsg(e))); }, [action]);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">System logs</h1>
      <select aria-label="Action filter" className="input w-auto" value={action} onChange={(e) => setAction(e.target.value)}>{ACTIONS.map((a) => <option key={a} value={a}>{a || "All actions"}</option>)}</select>
      {error && <p role="alert" className="text-red-600">{error}</p>}
      {!rows ? <Spinner /> : (
        <div className="card overflow-x-auto p-0"><table className="w-full text-left text-sm">
          <thead className="bg-slate-100 text-xs uppercase text-slate-500"><tr><th className="p-3">Time</th><th>Action</th><th>User</th><th>Detail</th></tr></thead>
          <tbody>{rows.map((r) => <tr key={r.id} className="border-t"><td className="p-3 whitespace-nowrap">{new Date(r.created_at).toLocaleString()}</td><td>{r.action}</td><td>{r.user || "-"}</td><td>{r.detail}</td></tr>)}</tbody></table></div>
      )}
    </div>
  );
}
