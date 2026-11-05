import { useState } from "react";
import { api, errMsg } from "../api";

const REASONS = ["Fake News", "Misleading Information", "Spam", "Hate Speech", "Manipulated Media", "Other"];

export default function ReportModal({ postId, onClose }) {
  const [reason, setReason] = useState(REASONS[0]);
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      await api.post("/reports", { post_id: postId, reason, description });
      onClose("Report submitted. A moderator will review it.");
    } catch (err) { setError(errMsg(err)); } finally { setBusy(false); }
  };

  return (
    <div className="fixed inset-0 z-20 flex items-center justify-center bg-black/40 p-4" role="dialog" aria-modal="true" aria-label="Report post">
      <form onSubmit={submit} className="card w-full max-w-md space-y-3">
        <h2 className="text-lg font-semibold">Report this post</h2>
        <div><label className="label" htmlFor="reason">Reason</label>
          <select id="reason" className="input" value={reason} onChange={(e) => setReason(e.target.value)}>{REASONS.map((r) => <option key={r}>{r}</option>)}</select></div>
        <div><label className="label" htmlFor="desc">Details (optional)</label>
          <textarea id="desc" className="input" rows={3} maxLength={1000} value={description} onChange={(e) => setDescription(e.target.value)} /></div>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <div className="flex justify-end gap-2">
          <button type="button" className="btn-secondary" onClick={() => onClose()}>Cancel</button>
          <button className="btn-primary" disabled={busy}>{busy ? "Submitting..." : "Submit report"}</button>
        </div>
      </form>
    </div>
  );
}
