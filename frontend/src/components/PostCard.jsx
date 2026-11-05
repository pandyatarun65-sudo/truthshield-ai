import { useState } from "react";
import { Link } from "react-router-dom";
import { api, errMsg, mediaUrl } from "../api";
import StatusBadge from "./StatusBadge";
import ReportModal from "./ReportModal";

export function Media({ post }) {
  const url = mediaUrl(post.media_url);
  if (!url) return null;
  if (post.media_type === "image") return <img src={url} alt="Post attachment" className="mt-3 max-h-96 rounded-lg" />;
  if (post.media_type === "video") return <video src={url} controls className="mt-3 max-h-96 w-full rounded-lg" />;
  return <audio src={url} controls className="mt-3 w-full" />;
}

export default function PostCard({ post: initial }) {
  const [post, setPost] = useState(initial);
  const [reporting, setReporting] = useState(false);
  const [msg, setMsg] = useState("");

  const like = async () => {
    try {
      const { data } = await api.post(`/posts/${post.id}/like`);
      setPost({ ...post, liked_by_me: data.liked, likes_count: data.likes_count });
    } catch (e) { setMsg(errMsg(e)); }
  };
  const share = async () => {
    try {
      const { data } = await api.post(`/posts/${post.id}/share`);
      setPost({ ...post, shares_count: data.shares_count });
      setMsg("Shared (simulation).");
    } catch (e) { setMsg(errMsg(e)); }
  };

  return (
    <article className="card">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-100 font-bold text-indigo-700">{post.author.username[0].toUpperCase()}</div>
        <div className="flex-1">
          <div className="font-semibold">@{post.author.username}</div>
          <div className="text-xs text-slate-500">{new Date(post.created_at).toLocaleString()} · {post.category}</div>
        </div>
        <StatusBadge post={post} />
      </div>
      {post.status === "WARNING" && <p className="mt-3 rounded-lg bg-amber-50 p-2 text-sm text-amber-800">⚠ This information could not be fully verified.</p>}
      <p className="mt-3 whitespace-pre-wrap">{post.text}</p>
      <Media post={post} />
      <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
        <button className="btn-secondary" onClick={like} aria-pressed={post.liked_by_me}>{post.liked_by_me ? "♥" : "♡"} Like ({post.likes_count})</button>
        <Link className="btn-secondary" to={`/post/${post.id}`}>💬 Comment ({post.comments_count})</Link>
        <button className="btn-secondary" onClick={share}>↗ Share ({post.shares_count})</button>
        <button className="btn-secondary" onClick={() => setReporting(true)}>⚑ Report</button>
        <Link className="ml-auto text-indigo-700 underline" to={`/post/${post.id}`}>View AI Analysis</Link>
      </div>
      {msg && <p className="mt-2 text-xs text-slate-500">{msg}</p>}
      {reporting && <ReportModal postId={post.id} onClose={(m) => { setReporting(false); if (m) setMsg(m); }} />}
    </article>
  );
}
