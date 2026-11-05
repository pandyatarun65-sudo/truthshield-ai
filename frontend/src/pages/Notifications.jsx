import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, errMsg } from "../api";
import Spinner from "../components/Spinner";

export default function Notifications() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const load = () => api.get("/notifications").then((r) => setData(r.data)).catch((e) => setError(errMsg(e)));
  useEffect(() => { load(); }, []);
  const read = async (id) => { await api.put(`/notifications/${id}/read`); load(); };
  const readAll = async () => { await api.put("/notifications/read-all"); load(); };
  if (error) return <p role="alert" className="text-red-600">{error}</p>;
  if (!data) return <Spinner />;
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between"><h1 className="text-xl font-bold">Notifications ({data.unread} unread)</h1>
        {data.unread > 0 && <button className="btn-secondary" onClick={readAll}>Mark all read</button>}</div>
      {data.items.length === 0 && <p className="text-slate-500">Nothing here yet.</p>}
      {data.items.map((n) => (
        <div key={n.id} className={`card flex items-start gap-3 ${n.is_read ? "opacity-70" : "border-indigo-300"}`}>
          <div className="flex-1"><p>{n.message}</p>
            <p className="text-xs text-slate-500">{n.type.replace("_", " ")} · {new Date(n.created_at).toLocaleString()} {n.post_id && <Link className="ml-2 text-indigo-700 underline" to={`/post/${n.post_id}`}>View post</Link>}</p></div>
          {!n.is_read && <button className="btn-secondary" onClick={() => read(n.id)}>Mark read</button>}
        </div>
      ))}
    </div>
  );
}
