import { useEffect, useState } from "react";
import { api, errMsg } from "../../api";
import BarChart from "../../components/BarChart";
import Spinner from "../../components/Spinner";

export default function Analytics() {
  const [a, setA] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { api.get("/admin/analytics").then((r) => setA(r.data)).catch((e) => setError(errMsg(e))); }, []);
  if (error) return <p role="alert" className="text-red-600">{error}</p>;
  if (!a) return <Spinner />;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Analytics</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <BarChart title="Fake news trend (average daily risk score)" data={a.fake_news_trend} color="bg-red-500" />
        <BarChart title="Risk distribution" data={a.risk_distribution} color="bg-amber-500" />
        <BarChart title="Reports by category" data={a.reports_by_category} color="bg-rose-500" />
        <BarChart title="AI vs human decision statistics" data={a.decision_stats} color="bg-emerald-500" />
        <BarChart title="Daily analysis count (14 days)" data={a.daily_analysis} />
      </div>
    </div>
  );
}
