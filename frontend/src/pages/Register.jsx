import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { errMsg } from "../api";
import { useAuth } from "../AuthContext";

export default function Register() {
  const { user, register } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState({ username: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  if (user) return <Navigate to="/" replace />;
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try { await register(f); nav("/"); } catch (err) { setError(errMsg(err)); } finally { setBusy(false); }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form onSubmit={submit} className="card w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-bold text-indigo-700">Create account</h1>
        <div><label className="label" htmlFor="u">Username</label><input id="u" required minLength={3} maxLength={30} pattern="[A-Za-z0-9_]+" className="input" value={f.username} onChange={set("username")} /></div>
        <div><label className="label" htmlFor="e">Email</label><input id="e" type="email" required className="input" value={f.email} onChange={set("email")} /></div>
        <div><label className="label" htmlFor="p">Password (min 8 characters)</label><input id="p" type="password" required minLength={8} maxLength={72} className="input" value={f.password} onChange={set("password")} /></div>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Creating account..." : "Register"}</button>
        <p className="text-sm">Already registered? <Link className="text-indigo-700 underline" to="/login">Login</Link></p>
      </form>
    </div>
  );
}
