import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../AuthContext";
import PostCard from "../components/PostCard";
import Spinner from "../components/Spinner";

export default function Home() {
  const { user } = useAuth();
  const [posts, setPosts] = useState(null);
  useEffect(() => { api.get("/posts", { params: { limit: 5 } }).then((r) => setPosts(r.data)).catch(() => setPosts([])); }, []);
  return (
    <div className="space-y-6">
      <section className="card bg-gradient-to-r from-indigo-600 to-indigo-800 text-white">
        <h1 className="text-2xl font-bold">Welcome, {user.username} 👋</h1>
        <p className="mt-2 text-sm text-indigo-100">Every post is analysed by TruthShield AI before it is published: ML model, knowledge-base fact check and rule-based signals produce a risk score and a clear explanation.</p>
        <Link to="/create-post" className="btn mt-4 bg-white text-indigo-700">Create Post</Link>
      </section>
      <section className="grid grid-cols-3 gap-3 text-center text-sm">
        <div className="card"><div className="text-2xl font-bold">{user.trust_score}</div>Trust score</div>
        <div className="card"><div className="text-2xl font-bold">{user.post_count}</div>Your posts</div>
        <div className="card"><div className="text-2xl font-bold">{user.report_count}</div>Your reports</div>
      </section>
      <h2 className="text-lg font-semibold">Latest posts</h2>
      {posts === null ? <Spinner /> : posts.map((p) => <PostCard key={p.id} post={p} />)}
      <Link to="/feed" className="text-indigo-700 underline">See the full feed →</Link>
    </div>
  );
}
