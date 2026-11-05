export default function Spinner({ label = "Loading..." }) {
  return (
    <div role="status" className="flex items-center justify-center gap-3 p-8 text-slate-500">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
      <span className="text-sm">{label}</span>
    </div>
  );
}
