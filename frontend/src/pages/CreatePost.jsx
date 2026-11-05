import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, errMsg } from "../api";
import AnalysisPanel from "../components/AnalysisPanel";
import Spinner from "../components/Spinner";

const CATS = ["General", "Health", "Science", "Technology", "Politics", "Sports", "Education", "Environment", "Entertainment"];
const OUTCOME = {
  PUBLISHED: ["✅ Your post looks safe.", "text-emerald-700"],
  WARNING: ["⚠️ This information could not be fully verified.", "text-amber-700"],
  UNDER_REVIEW: ["🔍 Your post has been sent for moderator review.", "text-blue-700"],
  BLOCKED: ["❌ This post has been blocked because of a high misinformation risk.", "text-red-700"],
};

export default function CreatePost() {
  const [text, setText] = useState("");
  const [category, setCategory] = useState("General");
  const [file, setFile] = useState(null);
  const [phase, setPhase] = useState("edit"); // edit | analyzing | preview | publishing | done
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const fileRef = useRef();
  const pick = (accept) => { fileRef.current.accept = accept; fileRef.current.click(); };

  const analyze = async (e) => {
    e.preventDefault();
    if (!text.trim()) return setError("Please write something first.");
    setError(""); setPhase("analyzing");
    try { setPreview((await api.post("/ai/analyze", { text })).data); setPhase("preview"); }
    catch (err) { setError(errMsg(err)); setPhase("edit"); }
  };

  const publish = async () => {
    setPhase("publishing"); setError("");
    const form = new FormData();
    form.append("text", text); form.append("category", category);
    if (file) form.append("file", file);
    try { setResult((await api.post("/posts", form)).data); setPhase("done"); }
    catch (err) { setError(errMsg(err)); setPhase("preview"); }
  };

  if (phase === "done") {
    const [msg, cls] = OUTCOME[result.status];
    return (
      <div className="card space-y-4">
        <p className={`text-lg font-semibold ${cls}`}>{msg}</p>
        <AnalysisPanel analysis={result.analysis} riskLevel={result.risk_level} />
        <div className="flex gap-2"><Link className="btn-primary" to={`/post/${result.id}`}>View post</Link><Link className="btn-secondary" to="/feed">Go to feed</Link></div>
      </div>
    );
  }

  const busy = phase === "analyzing" || phase === "publishing";
  return (
    <div className="space-y-4">
      <form onSubmit={analyze} className="card space-y-3">
        <h1 className="text-xl font-bold">Create New Post</h1>
        <div><label className="label" htmlFor="text">What's on your mind?</label>
          <textarea id="text" className="input" rows={5} maxLength={5000} placeholder="Write something..." value={text} disabled={busy} onChange={(e) => { setText(e.target.value); if (phase === "preview") setPhase("edit"); }} /></div>
        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn-secondary" onClick={() => pick("image/*")}>Upload Image</button>
          <button type="button" className="btn-secondary" onClick={() => pick("video/*")}>Upload Video</button>
          <button type="button" className="btn-secondary" onClick={() => pick("audio/*")}>Upload Audio</button>
          <input ref={fileRef} type="file" hidden onChange={(e) => setFile(e.target.files[0] || null)} />
        </div>
        {file && <p className="text-sm text-slate-600">Attached: {file.name} <button type="button" className="text-red-600 underline" onClick={() => setFile(null)}>remove</button></p>}
        <div><label className="label" htmlFor="cat">Category</label>
          <select id="cat" className="input" value={category} onChange={(e) => setCategory(e.target.value)}>{CATS.map((c) => <option key={c}>{c}</option>)}</select></div>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{phase === "analyzing" ? "Analyzing content..." : "Analyze & Publish"}</button>
      </form>

      {phase === "analyzing" && <Spinner label="Analyzing content..." />}
      {phase === "publishing" && <Spinner label="Publishing..." />}
      {(phase === "preview") && (
        <div className="card space-y-4">
          <AnalysisPanel analysis={preview} riskLevel={preview.risk_level} />
          {preview.post_status === "PUBLISHED" && <button className="btn-success" onClick={publish}>Publish</button>}
          {preview.post_status === "WARNING" && (<><p className="text-amber-700">⚠️ This information could not be fully verified.</p><button className="btn-primary" onClick={publish}>Publish Anyway</button></>)}
          {preview.post_status === "UNDER_REVIEW" && (<><p className="text-blue-700">🔍 Posting will send your post for moderator review.</p><button className="btn-primary" onClick={publish}>Submit for review</button></>)}
          {preview.post_status === "BLOCKED" && (<><p className="text-red-700">❌ This post has a high misinformation risk and will be blocked and sent to a moderator.</p><button className="btn-secondary" onClick={publish}>Submit anyway for moderator review</button></>)}
          <p className="text-xs text-slate-500">The final decision is made again on the server when you publish.</p>
        </div>
      )}
    </div>
  );
}
