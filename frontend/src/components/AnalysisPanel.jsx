import { RiskBadge } from "./StatusBadge";

const Stat = ({ label, value }) => (
  <div className="rounded-lg bg-slate-50 p-3 text-center">
    <div className="text-xl font-bold">{value}%</div>
    <div className="text-xs text-slate-500">{label}</div>
  </div>
);

/** Explainable-AI panel used on Create Post and Post Details. */
export default function AnalysisPanel({ analysis, riskLevel }) {
  if (!analysis) return <p className="text-sm text-slate-500">No AI analysis available.</p>;
  const level = riskLevel || analysis.risk_level;
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">AI Analysis</h3>
        <div className="flex items-center gap-2 text-sm">Risk score <b>{analysis.risk_score}</b> <RiskBadge level={level} /></div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <Stat label="Fake news probability" value={Math.round(analysis.fake_probability)} />
        <Stat label="Credibility" value={Math.round(analysis.credibility)} />
        <Stat label="Confidence" value={Math.round(analysis.confidence)} />
      </div>
      {analysis.fact && (
        <p className="text-sm"><b>Fact check:</b> {analysis.fact.status} {analysis.fact.source ? `(source: ${analysis.fact.source})` : ""}</p>
      )}
      <div>
        <p className="mb-1 text-sm font-medium">Reasons</p>
        <ol className="list-decimal space-y-1 pl-5 text-sm text-slate-700">
          {analysis.reasons.map((r, i) => <li key={i}>{r}</li>)}
        </ol>
      </div>
      <p className="text-xs text-slate-500">Academic prototype: AI results are probabilistic and may be wrong. "Unverified" does not mean "false".</p>
    </div>
  );
}
