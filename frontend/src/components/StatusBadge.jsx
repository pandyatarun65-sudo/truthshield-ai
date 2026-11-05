const STYLES = {
  verified: ["✓ Verified", "bg-emerald-100 text-emerald-800"],
  unverified: ["⚠ Unverified", "bg-slate-100 text-slate-700"],
  warning: ["⚠ Warning", "bg-amber-100 text-amber-800"],
  review: ["🔍 Under Review", "bg-blue-100 text-blue-800"],
  blocked: ["✕ Blocked", "bg-red-100 text-red-800"],
  removed: ["Removed", "bg-slate-200 text-slate-600"],
};

export function badgeKey(post) {
  if (post.status === "WARNING") return "warning";
  if (post.status === "UNDER_REVIEW") return "review";
  if (post.status === "BLOCKED") return "blocked";
  if (post.status === "REMOVED") return "removed";
  return post.fact_status === "TRUE" ? "verified" : "unverified";
}

export default function StatusBadge({ post }) {
  const [text, cls] = STYLES[badgeKey(post)];
  return <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>{text}</span>;
}

const RISK = { SAFE: "bg-emerald-100 text-emerald-800", WARNING: "bg-amber-100 text-amber-800", REVIEW: "bg-orange-100 text-orange-800", HIGH_RISK: "bg-red-100 text-red-800" };
export const RiskBadge = ({ level }) => (
  <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${RISK[level] || "bg-slate-100"}`}>{(level || "").replace("_", " ")}</span>
);
