import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, errMsg } from "../api";
import { useAuth } from "../AuthContext";
import AnalysisPanel from "../components/AnalysisPanel";
import PostCard from "../components/PostCard";
import Spinner from "../components/Spinner";

export default function PostDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const nav = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = async () => {
    try {
      setPost((await api.get(`/posts/${id}`)).data);
      setComments((await api.get(`/posts/${id}/comments`)).data);
    } catch (e) { setError(errMsg(e)); }
  };
  useEffect(() => { load(); }, [id]); // eslint-disable-line

  const comment = async (e) => {
    e.preventDefault(); setBusy(true); setError("");
    try { await api.post(`/posts/${id}/comments`, { text }); setText(""); await load(); }
    catch (err) { setError(errMsg(err)); } finally { setBusy(false); }
  };
  const remove = async () => {
    if (!confirm("Delete this post?")) return;
    try { await api.delete(`/posts/${id}`); nav("/feed"); } catch (e) { setError(errMsg(e)); }
  };

  if (error && !post) return <p role="alert" className="text-red-600">{error}</p>;
  if (!post) return <Spinner />;
  const open = ["PUBLISHED", "WARNING"].includes(post.status);
  return (
    <div className="space-y-4">
      <PostCard key={post.id + post.status} post={post} />
      {!open && <p className="rounded-lg bg-blue-50 p-3 text-sm text-blue-800">This post is not public (status: {post.status.replace("_", " ")}). Only you and moderators can see it.</p>}
      <section className="card"><AnalysisPanel analysis={post.analysis} riskLevel={post.risk_level} /></section>
      {(user.id === post.author.id || user.role !== "user") && post.status !== "REMOVED" && <button className="btn-danger" onClick={remove}>Delete post</button>}
      <section className="card space-y-3">
        <h2 className="font-semibold">Comments ({comments.length})</h2>
        {comments.map((c) => <div key={c.id} className="rounded-lg bg-slate-50 p-2 text-sm"><b>@{c.username}</b> <span className="text-xs text-slate-500">{new Date(c.created_at).toLocaleString()}</span><p>{c.text}</p></div>)}
        {open && (
          <form onSubmit={comment} className="flex gap-2">
            <input aria-label="Write a comment" required maxLength={500} className="input" placeholder="Write a comment..." value={text} onChange={(e) => setText(e.target.value)} />
            <button className="btn-primary" disabled={busy}>{busy ? "..." : "Send"}</button>
          </form>
        )}
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
      </section>
    </div>
  );
}
