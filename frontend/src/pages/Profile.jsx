import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, errMsg, mediaUrl } from "../api";
import { useAuth } from "../AuthContext";
import PostCard from "../components/PostCard";
import Spinner from "../components/Spinner";

export default function Profile() {
  const { user, refresh } = useAuth();
  const [username, setUsername] = useState(user.username);
  const [posts, setPosts] = useState(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const fileRef = useRef();

  useEffect(() => { api.get("/posts", { params: { mine: true, limit: 50 } }).then((r) => setPosts(r.data)).catch(() => setPosts([])); }, []);

  const save = async (e) => {
    e.preventDefault(); setBusy(true); setMsg("");
    try { await api.put(`/users/${user.id}`, { username }); await refresh(); setMsg("Profile updated."); }
    catch (err) { setMsg(errMsg(err)); } finally { setBusy(false); }
  };
  const upload = async (e) => {
    const f = e.target.files[0]; if (!f) return;
    const form = new FormData(); form.append("file", f); setBusy(true);
    try { await api.post(`/users/${user.id}/photo`, form); await refresh(); setMsg("Photo updated."); }
    catch (err) { setMsg(errMsg(err)); } finally { setBusy(false); }
  };

  return (
    <div className="space-y-4">
      <section className="card flex flex-wrap items-center gap-4">
        {user.photo_url ? <img src={mediaUrl(user.photo_url)} alt="Profile" className="h-20 w-20 rounded-full object-cover" />
          : <div className="flex h-20 w-20 items-center justify-center rounded-full bg-indigo-100 text-3xl font-bold text-indigo-700">{user.username[0].toUpperCase()}</div>}
        <div className="flex-1">
          <h1 className="text-xl font-bold">@{user.username}</h1>
          <p className="text-sm text-slate-500">{user.email} · role: {user.role}</p>
          <p className="mt-1 text-sm">Trust score <b>{user.trust_score}</b> · Posts <b>{user.post_count}</b> · Reports <b>{user.report_count}</b></p>
        </div>
        <button className="btn-secondary" onClick={() => fileRef.current.click()} disabled={busy}>Change photo</button>
        <input ref={fileRef} type="file" accept="image/*" hidden onChange={upload} />
      </section>
      <form onSubmit={save} className="card flex flex-wrap items-end gap-2">
        <div className="flex-1"><label className="label" htmlFor="un">Username</label><input id="un" className="input" minLength={3} maxLength={30} pattern="[A-Za-z0-9_]+" value={username} onChange={(e) => setUsername(e.target.value)} /></div>
        <button className="btn-primary" disabled={busy}>{busy ? "Saving..." : "Save"}</button>
        {msg && <p className="w-full text-sm text-slate-600" role="status">{msg}</p>}
      </form>
      <h2 className="flex items-center justify-between text-lg font-semibold">Your posts <Link to="/reports" className="text-sm font-normal text-indigo-700 underline">My report history</Link></h2>
      {posts === null ? <Spinner /> : posts.length === 0 ? <p className="text-slate-500">You have not posted yet.</p> : posts.map((p) => <PostCard key={p.id} post={p} />)}
    </div>
  );
}
