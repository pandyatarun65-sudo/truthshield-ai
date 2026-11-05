/** Tiny dependency-free bar chart. data = [{label, value}] */
export default function BarChart({ title, data, color = "bg-indigo-500" }) {
  const max = Math.max(1, ...data.map((d) => d.value));
  return (
    <section className="card">
      <h3 className="mb-3 font-semibold">{title}</h3>
      {data.length === 0 && <p className="text-sm text-slate-500">No data yet.</p>}
      <div className="space-y-2">
        {data.map((d) => (
          <div key={d.label} className="flex items-center gap-2 text-xs">
            <span className="w-28 shrink-0 truncate text-slate-600" title={d.label}>{d.label}</span>
            <div className="h-4 flex-1 rounded bg-slate-100"><div className={`h-4 rounded ${color}`} style={{ width: `${(d.value / max) * 100}%` }} /></div>
            <span className="w-8 text-right font-semibold">{d.value}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
