import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { errMsg } from "../api";
import { useAuth } from "../AuthContext";

export default function Login() {
  const { user, login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  if (user) return <Navigate to="/" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try { const u = await login(email, password); nav(["admin", "moderator"].includes(u.role) ? "/admin" : "/"); }
    catch (err) { setError(errMsg(err)); } finally { setBusy(false); }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form onSubmit={submit} className="card w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-bold text-indigo-700">🛡 TruthShield AI</h1>
        <p className="text-sm text-slate-500">Log in to continue. (Academic prototype)</p>
        <div><label className="label" htmlFor="email">Email</label><input id="email" type="email" required className="input" value={email} onChange={(e) => setEmail(e.target.value)} /></div>
        <div><label className="label" htmlFor="pw">Password</label><input id="pw" type="password" required className="input" value={password} onChange={(e) => setPassword(e.target.value)} /></div>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Logging in..." : "Login"}</button>
        <p className="text-sm">No account? <Link className="text-indigo-700 underline" to="/register">Register</Link></p>
      </form>
    </div>
  );
}
