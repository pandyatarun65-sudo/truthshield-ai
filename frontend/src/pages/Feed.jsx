import { useEffect, useState } from "react";
import { api, errMsg } from "../api";
import PostCard from "../components/PostCard";
import Spinner from "../components/Spinner";

const CATS = ["", "General", "Health", "Science", "Technology", "Politics", "Sports", "Education", "Environment", "Entertainment"];

export default function Feed({ explore }) {
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("");
  const [posts, setPosts] = useState(null);
  const [error, setError] = useState("");

  const load = async () => {
    setPosts(null); setError("");
    try { setPosts((await api.get("/posts", { params: { q: q || undefined, category: category || undefined, limit: 50 } })).data); }
    catch (e) { setError(errMsg(e)); setPosts([]); }
  };
  useEffect(() => { load(); }, [category, explore]); // eslint-disable-line

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">{explore ? "Explore" : "Feed"}</h1>
      <form className="flex flex-wrap gap-2" onSubmit={(e) => { e.preventDefault(); load(); }} role="search">
        <input aria-label="Search posts" className="input flex-1" placeholder="Search posts..." value={q} onChange={(e) => setQ(e.target.value)} />
        <select aria-label="Category" className="input w-auto" value={category} onChange={(e) => setCategory(e.target.value)}>
          {CATS.map((c) => <option key={c} value={c}>{c || "All categories"}</option>)}
        </select>
        <button className="btn-primary">Search</button>
      </form>
      {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
      {posts === null ? <Spinner /> : posts.length === 0 ? <p className="text-slate-500">No posts found.</p> : posts.map((p) => <PostCard key={p.id} post={p} />)}
    </div>
  );
}
