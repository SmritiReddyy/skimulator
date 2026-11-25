import type { Issue, Severity } from "../types";

const STYLES: Record<Severity, { badge: string; label: string }> = {
  critical: { badge: "bg-rose-100 text-rose-700", label: "Critical" },
  warning: { badge: "bg-amber-100 text-amber-700", label: "Warning" },
  info: { badge: "bg-sky-100 text-sky-700", label: "Tip" },
};

const ORDER: Severity[] = ["critical", "warning", "info"];

export default function IssueList({ issues }: { issues: Issue[] }) {
  if (issues.length === 0) {
    return (
      <p className="rounded-xl bg-emerald-50 p-4 text-emerald-700">
        No issues found. This resume should parse cleanly.
      </p>
    );
  }

  const sorted = [...issues].sort((a, b) => ORDER.indexOf(a.severity) - ORDER.indexOf(b.severity));

  return (
    <ul className="space-y-3">
      {sorted.map((issue) => (
        <li key={issue.id} className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2">
            <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${STYLES[issue.severity].badge}`}>
              {STYLES[issue.severity].label}
            </span>
            <h4 className="font-semibold">{issue.title}</h4>
          </div>
          <p className="mt-1.5 text-sm text-slate-600">{issue.detail}</p>
        </li>
      ))}
    </ul>
  );
}
