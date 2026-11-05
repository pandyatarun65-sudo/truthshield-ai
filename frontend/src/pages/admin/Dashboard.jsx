import { useEffect, useState } from "react";
import { api, errMsg } from "../../api";
import BarChart from "../../components/BarChart";
import Spinner from "../../components/Spinner";

const CARDS = [["total_users", "Total Users"], ["total_posts", "Total Posts"], ["fake_news_detected", "Fake News Detected"],
  ["posts_under_review", "Posts Under Review"], ["pending_reports", "Pending Reports"], ["blocked_posts", "Blocked Posts"],
  ["safe_posts", "Safe Posts"], ["warning_posts", "Warning Posts"]];

export default function Dashboard() {
  const [d, setD] = useState(null);
  const [a, setA] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([api.get("/admin/dashboard"), api.get("/admin/analytics")]).then(([x, y]) => { setD(x.data); setA(y.data); }).catch((e) => setError(errMsg(e)));
  }, []);
  if (error) return <p role="alert" className="text-red-600">{error}</p>;
  if (!d) return <Spinner />;
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {CARDS.map(([k, label]) => <div key={k} className="card"><div className="text-3xl font-bold text-indigo-700">{d[k]}</div><div className="text-sm text-slate-500">{label}</div></div>)}
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <BarChart title="Posts by risk level" data={a.risk_distribution} color="bg-amber-500" />
        <BarChart title="Reports by category" data={a.reports_by_category} color="bg-rose-500" />
        <BarChart title="Daily analysis count" data={a.daily_analysis.slice(-7)} />
      </div>
    </div>
  );
}
